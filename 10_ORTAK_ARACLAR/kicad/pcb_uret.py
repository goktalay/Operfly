"""Şematikten kart (PCB) dosyasının başlangıcını üretir: ayak izleri, ağlar, kart sınırı, yerleşim taslağı.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/pcb_uret.py <KART> <kök> [genişlik_mm]`
(ör. `python 10_ORTAK_ARACLAR/kicad/pcb_uret.py AIR operfly_air 60`). Çıktı: `out/pcb/<kök>.kicad_pcb` (depoya girmez).

NE YAPAR: şematiğin ağ listesini çıkarır, her elemanın ayak izini kütüphaneden yükler, uçlarına ağlarını atar,
elemanları şematik sayfasına göre gruplayıp çakışmadan raflara dizer, kart sınırını çizer.
NE YAPMAZ: yol çizmez, bakır alanı dökmez. Raf dizilimi mühendislik yerleşimi DEĞİLDİR (yalnızca tüm ayak izlerinin
ve ağların karta doğru geldiğini gösterir); gerçek yerleşim kart başına ayrıca yapılır.
"""
import os
import re
import subprocess
import sys

import pcbnew

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KICAD_FP = os.environ.get("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
ORTAK_FP = os.path.join(KOK, "01_DONANIM", "ORTAK_KUTUPHANE", "ayak_izleri", "operfly_ayak.pretty")
MM = pcbnew.FromMM


def ag_listesi(sema):
    yol = os.path.join(KOK, "out", "pcb", "_ag.net")
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", yol, sema], check=True, capture_output=True)
    t = open(yol, encoding="utf-8").read()
    elemanlar = []
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)(.*?)(?=\(comp\s*\(ref|\(libparts)', t, re.S):
        govde = m.group(3)
        fp = re.match(r'\s*\(footprint "([^"]*)"\)', govde)
        sayfa = re.search(r'\(sheetpath\s*\(names "([^"]*)"\)\s*\(tstamps "([^"]*)"\)', govde)
        kimlik = re.search(r'\(tstamps "([0-9a-f-]{36})"\)', govde)
        dnp = re.search(r'\(property\s*\(name "dnp"\)', govde) is not None
        elemanlar.append({"ref": m.group(1), "deger": m.group(2), "fp": fp.group(1) if fp else "", "sayfa": sayfa.group(1) if sayfa else "/", "dnp": dnp,
                         "bom_disi": re.search(r'\(property\s*\(name "exclude_from_bom"\)', govde) is not None,
                         "yol": ((sayfa.group(2) if sayfa else "/") + (kimlik.group(1) if kimlik else ""))})
    aglar = []
    for ad, govde in re.findall(r'\(net\s*\(code "?\d+"?\)\s*\(name "([^"]*)"\)(.*?)(?=\(net\s*\(code|\Z)', t, re.S):
        aglar.append((ad, re.findall(r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', govde)))
    return elemanlar, aglar


def ayak_izi(ad):
    kutuphane, isim = ad.split(":", 1)
    yol = ORTAK_FP if kutuphane == "operfly_ayak" else os.path.join(KICAD_FP, kutuphane + ".pretty")
    fp = pcbnew.FootprintLoad(yol, isim)
    if fp is None:
        raise SystemExit("ayak izi bulunamadı: %s" % ad)
    return fp


def uret(kart, kok, genislik=80.0, bosluk=1.0):
    sema = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_sch")
    elemanlar, aglar = ag_listesi(sema)
    cikti = os.path.join(KOK, "out", "pcb", kok + ".kicad_pcb")
    b = pcbnew.NewBoard(cikti)
    fpler = {}
    atanmamis = [e["ref"] for e in elemanlar if not e["fp"]]
    if atanmamis:
        print("UYARI: ayak izi atanmamış elemanlar (%d): %s" % (len(atanmamis), ", ".join(atanmamis[:20])))
    for e in elemanlar:
        if not e["fp"]:
            continue
        fp = ayak_izi(e["fp"])
        fp.SetReference(e["ref"])
        fp.SetValue(e["deger"])
        kutuphane, isim = e["fp"].split(":", 1)
        fp.SetFPID(pcbnew.LIB_ID(kutuphane, isim))
        fp.SetPath(pcbnew.KIID_PATH(e["yol"]))   # şematikteki sembole bağ (şematik-kart uyum denetimi için)
        fp.SetExcludedFromBOM(e["bom_disi"])
        if e["dnp"]:
            fp.SetDNP(True)
        b.Add(fp)
        fpler[e["ref"]] = (fp, e["sayfa"])
    eksik = []
    for ad, uclar in aglar:
        ag = pcbnew.NETINFO_ITEM(b, ad)
        b.Add(ag)
        for ref, uc in uclar:
            if ref not in fpler:
                continue
            bulundu = False
            for pad in fpler[ref][0].Pads():
                if pad.GetNumber() == uc:
                    pad.SetNet(ag)
                    bulundu = True
            if not bulundu:
                eksik.append("%s.%s (%s)" % (ref, uc, ad))
    # Raf dizilimi: sayfa sayfa, büyükten küçüğe; her eleman avlu (ya da uç) kutusuna göre yan yana.
    x0, y0 = 5.0, 5.0
    x, y, satir_h = x0, y0, 0.0
    for sayfa in sorted({s for _, s in fpler.values()}):
        grup = [fp for fp, s in fpler.values() if s == sayfa]
        grup.sort(key=lambda f: -(f.GetBoundingBox(False).GetWidth() * f.GetBoundingBox(False).GetHeight()))
        for fp in grup:
            kutu = fp.GetBoundingBox(False)
            w, h = pcbnew.ToMM(kutu.GetWidth()) + bosluk, pcbnew.ToMM(kutu.GetHeight()) + bosluk
            if x + w > x0 + genislik and x > x0:
                x, y, satir_h = x0, y + satir_h, 0.0
            merkez = fp.GetPosition()
            dx, dy = pcbnew.ToMM(merkez.x - kutu.GetLeft()), pcbnew.ToMM(merkez.y - kutu.GetTop())
            fp.SetPosition(pcbnew.VECTOR2I(MM(x + dx), MM(y + dy)))
            x, satir_h = x + w, max(satir_h, h)
        x, y, satir_h = x0, y + satir_h + 2.0, 0.0
    w_kart, h_kart = genislik + 10.0, y + 3.0
    kose = [(0, 0), (w_kart, 0), (w_kart, h_kart), (0, h_kart)]
    for (ax, ay), (bx, by) in zip(kose, kose[1:] + kose[:1]):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay)))
        s.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)
    pcbnew.SaveBoard(cikti, b)
    print("yazıldı: %s | %d eleman, %d ağ, taslak kart %.0f x %.0f mm" % (os.path.relpath(cikti, KOK), len(fpler), b.GetNetCount() - 1, w_kart, h_kart))
    if eksik:
        print("UYARI: ayak izinde bulunmayan uçlar (%d): %s" % (len(eksik), ", ".join(eksik[:12])))
    return cikti, eksik


if __name__ == "__main__":
    uret(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 80.0)
