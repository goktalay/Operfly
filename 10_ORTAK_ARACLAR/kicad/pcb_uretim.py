"""Çizilmiş karttan üretim dosyalarını çıkarır: Gerber, delik, dizgi (yerleşim) ve malzeme listesi.

Çalıştırma: depo kökünden
    python 10_ORTAK_ARACLAR/kicad/pcb_uretim.py <KART> <kök>          tek kart
    python 10_ORTAK_ARACLAR/kicad/pcb_uretim.py hepsi                 çizilmiş bütün kartlar
    ... --zorla                                                       denetimden geçmeyen kartı da çıkar
Çıktı: `out/uretim/<kök>/` (gerber/, delik/, dizgi/, <kök>_malzeme.csv, OKU.md) ve `out/uretim/<kök>_uretim.zip`.
Çıktılar depoya girmez.

KORUMALAR (varsayılan olarak üretim dosyası ÇIKARILMAZ):
  - DRC'de ihlal ya da bağlanmamış uç varsa (kart tamamlanmamıştır),
  - şematik-kart uyumu bozuksa,
  - kartın `pcb_ayar.py` dosyasında "uretilmez": "<neden>" yazıyorsa (ör. güç yolları yetersiz kart).
`--zorla` bu korumaları aşar; o zaman neden OKU.md dosyasının başına UYARI olarak yazılır.

Her pakete, kartın README'sindeki "Kart çizimi (otomatik)" bölümü OKU.md olarak eklenir: kartlar otomatik
çizilmiştir ve üretimden önce bir kart tasarımcısınca gözden geçirilmelidir.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_yerlesim  # noqa: E402

KOK = pcb_yerlesim.KOK
KARTLAR = [("CORE", "operfly_core"), ("POWER", "operfly_power"), ("HUB", "operfly_hub"), ("PC_ADAPTOR", "operfly_pc_adaptor"),
           ("NAV", "operfly_nav"), ("RX", "operfly_rx"), ("RADIO", "operfly_radio"), ("KUMANDA_GIRIS", "operfly_kumanda_giris"),
           ("KUMANDA_12", "operfly_pilot12"), ("AIR", "operfly_air"), ("ENGINE", "operfly_engine"), ("VISION", "operfly_vision"),
           ("RANGE", "operfly_range"), ("CELL", "operfly_cell"), ("KUMANDA_T", "operfly_pilott"), ("KUMANDA_PRO", "operfly_pilotpro"),
           ("BASE", "operfly_base"), ("YER_RADYO", "operfly_groundradio"), ("TRACKER", "operfly_tracker"), ("SHIELD", "operfly_shield")]


def calistir(komut):
    s = subprocess.run(komut, capture_output=True, text=True)
    if s.returncode != 0:
        raise SystemExit("komut başarısız: %s\n%s" % (" ".join(komut[:5]), (s.stdout + s.stderr)[-600:]))
    return s


def denetle(kart, kok, pcb):
    """Üretime engel nedenleri döndürür (boş liste = engel yok)."""
    engel = []
    rapor = os.path.join(KOK, "out", "uretim", kok + "_drc.json")
    os.makedirs(os.path.dirname(rapor), exist_ok=True)
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", rapor, pcb], capture_output=True, text=True)
    r = json.load(open(rapor, encoding="utf-8"))
    hata = [v for v in r.get("violations", []) if v["severity"] == "error"]
    if hata:
        engel.append("DRC'de %d ihlal var" % len(hata))
    if r.get("unconnected_items"):
        engel.append("%d bağlantı çizilmemiş (kart tamamlanmadı)" % len(r["unconnected_items"]))
    if r.get("schematic_parity"):
        engel.append("şematik-kart uyumunda %d fark var" % len(r["schematic_parity"]))
    neden = pcb_yerlesim.ayar_oku(kart).get("uretilmez")
    if neden:
        engel.append("üretilmez olarak işaretli: " + neden)
    return engel


def uret(kart, kok, zorla=False):
    klasor = os.path.join(KOK, "01_DONANIM", kart)
    pcb = os.path.join(klasor, "kicad", kok + ".kicad_pcb")
    sema = os.path.join(klasor, "kicad", kok + ".kicad_sch")
    if not os.path.exists(pcb):
        print("%-14s kart dosyası yok, atlandı" % kart)
        return None
    engel = denetle(kart, kok, pcb)
    if engel and not zorla:
        print("%-14s ÜRETİM DOSYASI ÇIKARILMADI: %s" % (kart, "; ".join(engel)))
        return None
    cikti = os.path.join(KOK, "out", "uretim", kok)
    shutil.rmtree(cikti, ignore_errors=True)
    for alt in ("gerber", "delik", "dizgi"):
        os.makedirs(os.path.join(cikti, alt))
    b = pcbnew.LoadBoard(pcb)
    n = b.GetCopperLayerCount()
    bakir = ["F.Cu"] + ["In%d.Cu" % i for i in range(1, n - 1)] + ["B.Cu"]
    katmanlar = bakir + ["F.Paste", "B.Paste", "F.SilkS", "B.SilkS", "F.Mask", "B.Mask", "Edge.Cuts"]
    calistir(["kicad-cli", "pcb", "export", "gerbers", "-o", os.path.join(cikti, "gerber") + os.sep, "--layers", ",".join(katmanlar),
              "--subtract-soldermask", "--check-zones", pcb])
    calistir(["kicad-cli", "pcb", "export", "drill", "-o", os.path.join(cikti, "delik") + os.sep, "--format", "excellon",
              "--excellon-units", "mm", "--excellon-separate-th", "--generate-map", "--map-format", "gerberx2", pcb])
    calistir(["kicad-cli", "pcb", "export", "pos", "-o", os.path.join(cikti, "dizgi", kok + "_yerlesim.csv"), "--format", "csv",
              "--units", "mm", "--side", "both", "--exclude-dnp", pcb])
    calistir(["kicad-cli", "sch", "export", "bom", "-o", os.path.join(cikti, kok + "_malzeme.csv"),
              "--fields", "Reference,Value,Footprint,${QUANTITY},${DNP}", "--labels", "Referans,Deger,Ayak izi,Adet,Takilmaz",
              "--group-by", "Value,Footprint,${DNP}", sema])
    # OKU.md: uyarılar + kart bilgisi + README'deki kart çizimi bölümü
    kutu = b.GetBoardEdgesBoundingBox()
    ayar = pcb_yerlesim.ayar_oku(kart)
    ac, yl, gc, dl = ayar.get("sinif") or pcb_yerlesim.SINIFLAR["Default"]
    dnp = len([f for f in b.GetFootprints() if f.IsDNP()])
    t = "# %s — üretim dosyaları\n\n" % kok
    if engel:
        t += "**UYARI: bu paket korumalar aşılarak (`--zorla`) üretildi. Engel: %s. BU DOSYALARLA ÜRETİM YAPILMAZ.**\n\n" % "; ".join(engel)
    t += ("**Bu kart otomatik çizilmiştir; bir kart tasarımcısı gözden geçirmeden üretime verilmemelidir.** "
          "Aşağıdaki \"Kart çizimi\" bölümünde üretimden önce bakılacak noktalar yazılıdır.\n\n")
    t += "## Üreticiye verilecek bilgiler\n\n"
    t += "- Kart ölçüsü: %.0f x %.0f mm; %d bakır katman; kalınlık 1,6 mm (katman dizilimi üreticinin standart %d katman dizilimi; empedans denetimi istenmedi).\n" % (
        pcbnew.ToMM(kutu.GetWidth()) - 0.1, pcbnew.ToMM(kutu.GetHeight()) - 0.1, n, n)
    t += ("- En küçük yol %.3f mm, en küçük açıklık %.3f mm, en küçük geçiş %.2f mm çap / %.2f mm delik" % (min(yl, 0.2), ac, gc, dl)).replace(".", ",") + ".\n"
    t += "- Katman sırası (üstten alta): %s.\n" % ", ".join(bakir)
    t += "- Elemanların tamamı üst yüzde. Takılmayacak (DNP) eleman sayısı: %d (dizgi ve malzeme dosyalarında ayrıca belirtilir).\n\n" % dnp
    t += "## Dosyalar\n\n- `gerber/`: bakır katmanlar, lehim maskesi, lehim pastası, serigrafi, kart sınırı (Gerber X2).\n"
    t += "- `delik/`: delik dosyaları (Excellon, mm; kaplamalı ve kaplamasız ayrı) ve delik haritası.\n"
    t += "- `dizgi/%s_yerlesim.csv`: eleman konumları ve açıları (mm; DNP elemanlar hariç).\n" % kok
    t += "- `%s_malzeme.csv`: malzeme listesi (değer ve ayak izine göre gruplanmış). Üretici parça numaraları için `13_DOKUMANTASYON/Operfly_BOM.xlsx` dosyasına bakılır.\n\n" % kok
    okuma = open(os.path.join(klasor, "README.md"), encoding="utf-8").read()
    i = okuma.find("\n## Kart çizimi")
    if i >= 0:
        t += okuma[i + 1:].rstrip("\n") + "\n"
    open(os.path.join(cikti, "OKU.md"), "w", encoding="utf-8", newline="\n").write(t)
    # Paket
    paket = os.path.join(KOK, "out", "uretim", kok + "_uretim.zip")
    with zipfile.ZipFile(paket, "w", zipfile.ZIP_DEFLATED) as z:
        for kokdizin, _, dosyalar in os.walk(cikti):
            for d in sorted(dosyalar):
                yol = os.path.join(kokdizin, d)
                z.write(yol, os.path.join(kok, os.path.relpath(yol, cikti)))
    gerber = len(os.listdir(os.path.join(cikti, "gerber")))
    delik = [d for d in os.listdir(os.path.join(cikti, "delik")) if d.endswith(".drl")]
    satir = sum(1 for _ in open(os.path.join(cikti, "dizgi", kok + "_yerlesim.csv"), encoding="utf-8")) - 1
    print("%-14s %d katman, %d gerber, %d delik dosyası, %d dizgi satırı, paket %d kB%s"
          % (kart, n, gerber, len(delik), satir, os.path.getsize(paket) // 1024, "  [ZORLA: %s]" % "; ".join(engel) if engel else ""))
    return paket


if __name__ == "__main__":
    arg = [a for a in sys.argv[1:] if a != "--zorla"]
    zorla = "--zorla" in sys.argv
    if arg and arg[0] == "hepsi":
        for kart, kok in KARTLAR:
            uret(kart, kok, zorla)
    else:
        uret(arg[0], arg[1], zorla)
