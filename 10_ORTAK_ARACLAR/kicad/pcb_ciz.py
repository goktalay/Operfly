"""Yerleşimi yapılmış kartın yollarını otomatik çizer, bakır alanlarını döker, DRC çalıştırır.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py <KART> <kök> [deneme sayısı]`
(yerleşim + yol çizimi; temiz çıkmazsa başka tohumla yeniden dener). `... <KART> <kök> tek` yalnızca yol çizer
(önce `pcb_yerlesim.py` çalıştırılmış olmalıdır), `... <KART> <kök> drc` yalnızca denetler.

Yol çizici KiCad'in parçası değildir: dışarıdan bir Specctra yol çizicisi (DSN alır, SES verir) kullanılır.
Çalıştırılacak jar dosyasının yolu OPERFLY_YOL_CIZICI ortam değişkeninden okunur. Araç depoya EKLENMEZ
(GPL lisanslıdır; yalnızca araç olarak çalıştırılır, çıktısı olan kart dosyası bizim tasarımımızdır).
Araç ağ erişimi olmadan çalıştırılır.

Katman düzeni (4 katman): üst = eleman + sinyal, iç 1 = kesintisiz toprak, iç 2 = ana lojik beslemesi (+3V3)
düzlemi, alt = sinyal. Çizimden sonra üst ve alt katmanların boş yerlerine de toprak dökülür.

SONUÇ BİR MÜHENDİS ÇİZİMİ DEĞİLDİR: empedans denetimi, uzunluk eşleme, anahtarlamalı güç döngüleri, ısıl geçişler
ve RF kuralları gözetilmez. Üretimden önce gözden geçirilir.
"""
import json
import os
import subprocess
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_yerlesim  # noqa: E402

KOK = pcb_yerlesim.KOK
MM = pcbnew.FromMM
JAR = os.environ.get("OPERFLY_YOL_CIZICI", "")
TOPRAK = "GND"
KENAR_PAYI = 0.25   # mm; yol çizicinin kart kenarından ek uzaklığı


def kurallar(b, ayar):
    bds = b.GetDesignSettings()
    ns = bds.m_NetSettings
    siniflar = dict(pcb_yerlesim.SINIFLAR)
    siniflar.update(ayar.get("siniflar", {}))
    for ad, (aciklik, yol, gecis, delik) in siniflar.items():
        nc = ns.GetDefaultNetclass() if ad == "Default" else pcbnew.NETCLASS(ad)
        nc.SetClearance(MM(aciklik))
        nc.SetTrackWidth(MM(yol))
        nc.SetViaDiameter(MM(gecis))
        nc.SetViaDrill(MM(delik))
        if ad != "Default":
            ns.SetNetclass(ad, nc)
    ns.ClearNetclassPatternAssignments()
    duzlem_aglari = set(ayar["duzlemler"].values())
    guc = [n for n in b.GetNetsByName().keys() if str(n).startswith("+") and str(n) not in duzlem_aglari]
    for ag in sorted(set(str(n) for n in guc) | set(ayar["guc_aglari"])):
        ns.SetNetclassPatternAssignment(ag, "Guc")
    bds.m_TrackMinWidth = MM(0.127)
    bds.m_ViasMinSize = MM(0.45)
    bds.m_MinThroughDrill = MM(0.2)
    bds.m_CopperEdgeClearance = MM(0.25)
    bds.m_MinClearance = MM(0.125)
    bds.m_HoleClearance = MM(0.2)
    bds.m_HoleToHoleMin = MM(0.25)
    bds.m_ViasMinAnnularWidth = MM(0.1)


def alan_ekle(b, katman, ag, oncelik=0, pay=0.0):
    kutu = b.GetBoardEdgesBoundingBox()
    z = pcbnew.ZONE(b)
    z.SetLayer(katman)
    z.SetNetCode(b.GetNetcodeFromNetname(ag))
    z.SetAssignedPriority(oncelik)
    p = z.Outline()
    p.NewOutline()
    l, t, r, a = kutu.GetLeft() + MM(pay), kutu.GetTop() + MM(pay), kutu.GetRight() - MM(pay), kutu.GetBottom() - MM(pay)
    for x, y in ((l, t), (r, t), (r, a), (l, a)):
        p.Append(x, y)
    z.SetLocalClearance(MM(0.2))
    z.SetMinThickness(MM(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z


def ciz(kart, kok, tur=40, sure="00:20:00"):
    ayar = pcb_yerlesim.ayar_oku(kart)
    yol = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_pcb")
    b = pcbnew.LoadBoard(yol)
    for t in list(b.GetTracks()):
        b.Remove(t)
    for z in list(b.Zones()):
        b.Remove(z)
    kurallar(b, ayar)
    katman = b.GetCopperLayerCount()
    duzlemler = {}
    if katman >= 4:
        for ad, ag in ayar["duzlemler"].items():
            if b.FindNet(ag) is not None:
                duzlemler[ad] = ag
                alan_ekle(b, b.GetLayerID(ad), ag)
    pcbnew.SaveBoard(yol, b)
    b = pcbnew.LoadBoard(yol)
    is_dizini = os.path.join(KOK, "out", "pcb", "yol")
    os.makedirs(is_dizini, exist_ok=True)
    dsn, ses = os.path.join(is_dizini, kok + ".dsn"), os.path.join(is_dizini, kok + ".ses")
    if os.path.exists(ses):
        os.remove(ses)
    # Yol çizici kart kenarına yalnızca ağ açıklığı kadar yaklaşır; bakırı kenardan uzak tutmak için ona
    # kartın KENAR_PAYI kadar küçültülmüş sınırı verilir, sonra gerçek sınır geri konur.
    kenarlar = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    kutu = b.GetBoardEdgesBoundingBox()
    for d in kenarlar:
        b.Remove(d)
    l, u, r, a = kutu.GetLeft() + MM(0.05 + KENAR_PAYI), kutu.GetTop() + MM(0.05 + KENAR_PAYI), kutu.GetRight() - MM(0.05 + KENAR_PAYI), kutu.GetBottom() - MM(0.05 + KENAR_PAYI)
    gecici_kenar = []
    for (ax, ay), (bx, by) in (((l, u), (r, u)), ((r, u), (r, a)), ((r, a), (l, a)), ((l, a), (l, u))):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(ax, ay))
        s.SetEnd(pcbnew.VECTOR2I(bx, by))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)
        gecici_kenar.append(s)
    tamam = pcbnew.ExportSpecctraDSN(b, dsn)
    for s in gecici_kenar:
        b.Remove(s)
    for d in kenarlar:
        b.Add(d)
    if not tamam:
        raise SystemExit("DSN yazılamadı")
    if not JAR or not os.path.exists(JAR):
        raise SystemExit("yol çizici bulunamadı: OPERFLY_YOL_CIZICI ortam değişkeni jar dosyasını göstermeli")
    ortam = {k: v for k, v in os.environ.items() if k not in ("JAVA_TOOL_OPTIONS", "HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy")}
    gecici = os.path.join(is_dizini, "tmp_" + kok)
    os.makedirs(os.path.join(gecici, "freerouting"), exist_ok=True)
    json.dump({"gui": {"enabled": False}, "usage_and_diagnostic_data": {"disable_analytics": True},
               "profile": {"allow_telemetry": False, "allow_contact": False}, "api_server": {"enabled": False},
               "router": {"max_passes": tur, "job_timeout": sure, "max_threads": 1,
                          "optimizer": {"max_passes": 3, "max_threads": 1}}},
              open(os.path.join(gecici, "freerouting", "freerouting.json"), "w"))
    komut = ["java", "-Djava.awt.headless=true", "-Djava.io.tmpdir=" + gecici, "-Dhttp.proxyHost=", "-Dhttps.proxyHost=", "-jar", JAR,
             "--gui.enabled=false", "-da", "-de", dsn, "-do", ses, "-mp", str(tur), "--router.max_passes=%d" % tur]
    s = subprocess.run(komut, cwd=is_dizini, env=ortam, capture_output=True, text=True, timeout=4 * 3600)
    open(os.path.join(is_dizini, kok + ".log"), "w", encoding="utf-8").write(s.stdout + "\n" + s.stderr)
    if not os.path.exists(ses):
        print((s.stdout + s.stderr)[-1500:])
        raise SystemExit("yol çizici sonuç dosyası üretmedi")
    if not pcbnew.ImportSpecctraSES(b, ses):
        raise SystemExit("SES okunamadı")
    for k in ["F.Cu", "B.Cu"] + (["In2.Cu"] if katman >= 4 else []):
        if k not in duzlemler:
            alan_ekle(b, b.GetLayerID(k), TOPRAK)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    pcbnew.SaveBoard(yol, b)
    yol_sayisi = len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"])
    gecis = len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"])
    print("çizildi: %d yol parçası, %d geçiş" % (yol_sayisi, gecis))
    return drc(kart, kok)


def drc(kart, kok):
    yol = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_pcb")
    rapor = os.path.join(KOK, "out", "pcb", kok + "_drc.json")
    subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", rapor, yol], capture_output=True, text=True)
    r = json.load(open(rapor, encoding="utf-8"))
    say = {}
    for v in r.get("violations", []):
        say[(v["severity"], v["type"])] = say.get((v["severity"], v["type"]), 0) + 1
    baglanmamis = len(r.get("unconnected_items", []))
    parite = {}
    for v in r.get("schematic_parity", []):
        parite[v["type"]] = parite.get(v["type"], 0) + 1
    print("DRC: %d ihlal, %d bağlanmamış uç" % (len(r.get("violations", [])), baglanmamis))
    for (onem, tip), n in sorted(say.items()):
        print("   %-8s %-34s %d" % (onem, tip, n))
    for tip, n in sorted(parite.items()):
        print("   şematik uyumu: %-22s %d" % (tip, n))
    return r


def otomatik(kart, kok, deneme=5, tur=40, sure="00:20:00"):
    """Yerleşim + yol çizimi. Sonuç temiz değilse (bağlanmamış uç ya da ihlal) başka tohumla yeniden dener,
    en iyisini bırakır. Temiz çıkan tohum kartın pcb_ayar.py dosyasına "tohum" olarak yazılır ki sonuç yinelenebilsin."""
    import shutil
    ayar = pcb_yerlesim.ayar_oku(kart)
    yol = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_pcb")
    en_iyi = None
    for n in range(deneme):
        tohum = ayar["tohum"] + n
        pcb_yerlesim.yerlestir(kart, kok, {"tohum": tohum})
        r = ciz(kart, kok, tur, sure)
        puan = 100 * len(r.get("unconnected_items", [])) + len([v for v in r.get("violations", []) if v["severity"] == "error"])
        print("tohum %d: puan %d" % (tohum, puan))
        if en_iyi is None or puan < en_iyi[0]:
            en_iyi = (puan, tohum)
            shutil.copy(yol, yol + ".eniyi")
        if puan == 0:
            break
    shutil.move(yol + ".eniyi", yol)
    print("SONUÇ: tohum %d, puan %d" % (en_iyi[1], en_iyi[0]))
    return drc(kart, kok), en_iyi[1]


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[3] == "drc":
        drc(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 3 and sys.argv[3] == "tek":
        ciz(sys.argv[1], sys.argv[2])
    else:
        otomatik(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 5)
