"""Yerleşimi yapılmış kartın yollarını otomatik çizer, bakır alanlarını döker, DRC çalıştırır.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py <KART> <kök> [deneme sayısı]`
(yerleşim + yol çizimi; temiz çıkmazsa başka tohumla yeniden dener). `... <KART> <kök> tek` ayardaki tohumla
bir kez yerleştirip çizer, `... <KART> <kök> drc` yalnızca denetler.

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
KADEMELER = (0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)   # besleme yolu genişlik kademeleri (mm)
RF_DESENI = r"^(GNSS_|RADIO_|WB_|KUM_)?ANT_?\d(_RF)?$"   # anten ağları
RF_GENISLIK = 0.35


def kurallar(b, ayar):
    bds = b.GetDesignSettings()
    ns = bds.m_NetSettings
    aciklik, yol, gecis, delik = pcb_yerlesim.SINIFLAR["Default"]
    nc = ns.GetDefaultNetclass()
    nc.SetClearance(MM(aciklik))
    nc.SetTrackWidth(MM(yol))
    nc.SetViaDiameter(MM(gecis))
    nc.SetViaDrill(MM(delik))
    ns.ClearNetclassPatternAssignments()
    # Besleme ağları ("+" ile başlayanlar ve ayardaki guc_aglari): yol genişliği ağın en dar ucunu aşmayacak
    # biçimde seçilir (uçlar arası açıklık bozulmasın). Ayardaki "genislik" {ağ: mm} bunu ezer.
    duzlem_aglari = set(ayar["duzlemler"].values())
    en_dar = {}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            ag = p.GetNetname()
            if ag:
                en_dar[ag] = min(en_dar.get(ag, 99.0), pcbnew.ToMM(min(p.GetSize().x, p.GetSize().y)))
    guc = {ag for ag in en_dar if ag.startswith("+") and ag not in duzlem_aglari} | (set(ayar["guc_aglari"]) & set(en_dar))
    kullanilan = set()
    for ag in sorted(guc | set(ayar.get("genislik", {}))):
        if ag not in en_dar:
            continue
        w = ayar.get("genislik", {}).get(ag) or max([k for k in KADEMELER if k <= en_dar[ag] + 1e-6] or [0.2])
        ad = "Guc_%03d" % round(w * 100)
        if ad not in kullanilan:
            nc = pcbnew.NETCLASS(ad)
            nc.SetClearance(MM(aciklik))
            nc.SetTrackWidth(MM(w))
            nc.SetViaDiameter(MM(0.8 if w >= 0.4 else 0.6))
            nc.SetViaDrill(MM(0.4 if w >= 0.4 else 0.3))
            ns.SetNetclass(ad, nc)
            kullanilan.add(ad)
        ns.SetNetclassPatternAssignment(ag, ad)
    # Anten (RF) ağları: 4 katmanlı standart dizilimde yaklaşık 50 ohm veren genişlik (üreticinin katman
    # dizilimiyle hesaplanıp doğrulanacak); uzunluk ve geçiş sayısı gözetilmez.
    import re
    rf = [ag for ag in en_dar if re.search(RF_DESENI, ag) and ag not in guc]
    if rf:
        nc = pcbnew.NETCLASS("RF")
        nc.SetClearance(MM(max(aciklik, 0.2)))
        nc.SetTrackWidth(MM(RF_GENISLIK))
        nc.SetViaDiameter(MM(0.6))
        nc.SetViaDrill(MM(0.3))
        ns.SetNetclass("RF", nc)
        for ag in sorted(rf):
            ns.SetNetclassPatternAssignment(ag, "RF")
    bds.m_TrackMinWidth = MM(0.127)
    bds.m_ViasMinSize = MM(0.45)
    bds.m_MinThroughDrill = MM(0.2)
    bds.m_CopperEdgeClearance = MM(0.25)
    bds.m_MinClearance = MM(0.125)
    bds.m_HoleClearance = MM(0.19)   # KiCad kütüphanesindeki USB Type-C ayak izinin kendi uç-delik aralığı 0,194 mm
    bds.m_HoleToHoleMin = MM(0.25)
    bds.m_ViasMinAnnularWidth = MM(0.1)


def alan_ekle(b, katman, ag, oncelik=0, pay=0.0, tam=True, kutu_mm=None):
    kutu = b.GetBoardEdgesBoundingBox()
    z = pcbnew.ZONE(b)
    z.SetLayer(katman)
    z.SetNetCode(b.GetNetcodeFromNetname(ag))
    z.SetAssignedPriority(oncelik)
    p = z.Outline()
    p.NewOutline()
    l, t, r, a = kutu.GetLeft() + MM(pay), kutu.GetTop() + MM(pay), kutu.GetRight() - MM(pay), kutu.GetBottom() - MM(pay)
    if kutu_mm:
        l, t, r, a = max(l, MM(kutu_mm[0])), max(t, MM(kutu_mm[1])), min(r, MM(kutu_mm[2])), min(a, MM(kutu_mm[3]))
    for x, y in ((l, t), (r, t), (r, a), (l, a)):
        p.Append(x, y)
    # Açıklık ve en küçük kalınlık küçük tutulur: yan yana geçişlerin boşlukları birleşip düzlemi parçalamasın.
    # Dış katman dökümleri uçlara tam bağlanır (ince adımlı kılıflarda ısıl köprü kurulamıyor);
    # iç düzlemlerde yalnızca delikli uçlara ısıl köprü bırakılır.
    z.SetLocalClearance(MM(0.125))
    z.SetMinThickness(MM(0.13))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if tam else pcbnew.ZONE_CONNECTION_THT_THERMAL)
    z.SetThermalReliefGap(MM(0.25))
    z.SetThermalReliefSpokeWidth(MM(0.3))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    b.Add(z)
    return z


def ciz(kart, kok, tur=40, sure="00:20:00"):
    ayar = pcb_yerlesim.ayar_oku(kart)
    yol = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_pcb")
    b = pcbnew.LoadBoard(yol)
    if len(b.GetTracks()) or len(b.Zones()):
        raise SystemExit("kart zaten çizilmiş; önce pcb_yerlesim.py ile yerleşim yeniden üretilir")
    kurallar(b, ayar)
    katman = b.GetCopperLayerCount()
    duzlemler = {}
    if katman >= 4:
        for ad, ag in ayar["duzlemler"].items():
            if b.FindNet(ag) is not None:
                duzlemler[ad] = ag
                alan_ekle(b, b.GetLayerID(ad), ag, tam=False)
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
    komut = ["java", "-Djava.awt.headless=true", "-Djava.io.tmpdir=" + gecici,
             # Ağ erişimi kapalı: araç açılışta sürüm denetimi için dışarı çıkmak ister; ölü bir vekil adresi verilir.
             "-Dhttp.proxyHost=127.0.0.1", "-Dhttp.proxyPort=9", "-Dhttps.proxyHost=127.0.0.1", "-Dhttps.proxyPort=9", "-jar", JAR,
             "--gui.enabled=false", "-da", "-de", dsn, "-do", ses, "-mp", str(tur), "--router.max_passes=%d" % tur]
    # Yol çizici ilerleyemediği yerleşimde çok uzun süre dönebilir: eleman sayısına göre süre sınırı konur.
    sinir = ayar.get("sure_dk") or (8 + len(b.GetFootprints()) / 10.0)
    try:
        s = subprocess.run(komut, cwd=is_dizini, env=ortam, capture_output=True, text=True, timeout=sinir * 60)
        open(os.path.join(is_dizini, kok + ".log"), "w", encoding="utf-8").write(s.stdout + "\n" + s.stderr)
    except subprocess.TimeoutExpired:
        print("yol çizici %.0f dakikada bitiremedi" % sinir)
    if not os.path.exists(ses) or os.path.getsize(ses) == 0 or not pcbnew.ImportSpecctraSES(b, ses):
        # Yol çizici ilerleyemeyince sonuç yazmadan çıkar: bu deneme başarısız sayılır.
        print("yol çizici bu yerleşimi bitiremedi (sonuç dosyası yok)")
        return {"violations": [], "unconnected_items": [{}] * 999, "bitmedi": True}
    for k in ["F.Cu", "B.Cu"] + (["In2.Cu"] if katman >= 4 else []):
        if k not in duzlemler:
            alan_ekle(b, b.GetLayerID(k), TOPRAK)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.BuildConnectivity()
    pcbnew.SaveBoard(yol, b)
    yol_sayisi = len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"])
    gecis = len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"])
    print("çizildi: %d yol parçası, %d geçiş" % (yol_sayisi, gecis))
    r = drc(kart, kok, sessiz=True)
    # Düzlem onarımı: yan yana geçişlerin boşlukları iç düzlemi adalara bölebilir. Yol çizici düzlemi kesintisiz
    # saydığı için bu adalar bağlanmamış kalır. Kalan her bağlantı için alt (olmazsa üst) katmana, o iki noktayı
    # kaplayan küçük bir besleme yaması dökülür (toprak dökümünden öncelikli).
    yama_aglari = set(duzlemler.values()) - {TOPRAK}
    for deneme, (katman_adi, genis) in enumerate((("B.Cu", 2.0), ("F.Cu", 2.0), ("B.Cu", 5.0), ("F.Cu", 5.0))):
        kalan = [u for u in r.get("unconnected_items", []) if _ag(u) in yama_aglari]
        if not kalan:
            break
        for u in kalan:
            xs = [i["pos"]["x"] for i in u["items"]]
            ys = [i["pos"]["y"] for i in u["items"]]
            alan_ekle(b, b.GetLayerID(katman_adi), _ag(u), oncelik=1 + deneme,
                      kutu_mm=(min(xs) - genis, min(ys) - genis, max(xs) + genis, max(ys) + genis))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        b.BuildConnectivity()
        pcbnew.SaveBoard(yol, b)
        print("düzlem onarımı %d: %d yama (%s)" % (deneme + 1, len(kalan), katman_adi))
        r = drc(kart, kok, sessiz=True)
    return drc(kart, kok)


def _ag(u):
    import re
    m = re.search(r"\[([^\]]+)\]", u["items"][0]["description"])
    return m.group(1) if m else ""


def drc(kart, kok, sessiz=False):
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
    if sessiz:
        return r
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
        ek = {"tohum": tohum}
        if ayar["en"] is None and n >= 3:   # ölçüsü verilmemiş kartta üç denemeden sonra kart büyütülür
            ek["doluluk"] = ayar["doluluk"] * (0.85 if n < 5 else 0.72)
        pcb_yerlesim.yerlestir(kart, kok, ek)
        r = ciz(kart, kok, tur, sure)
        puan = 100 * len(r.get("unconnected_items", [])) + len([v for v in r.get("violations", []) if v["severity"] == "error"])
        print("tohum %d: puan %d" % (tohum, puan))
        if (en_iyi is None or puan < en_iyi[0]) and not r.get("bitmedi"):
            en_iyi = (puan, tohum)
            shutil.copy(yol, yol + ".eniyi")
        if puan == 0:
            break
    if en_iyi is None:
        print("SONUÇ: hiçbir denemede yol çizimi bitmedi")
        json.dump({"kart": kart, "kok": kok, "bitmedi": True}, open(os.path.join(KOK, "out", "pcb", kok + "_sonuc.json"), "w"))
        return None, None
    shutil.move(yol + ".eniyi", yol)
    print("SONUÇ: tohum %d, puan %d" % (en_iyi[1], en_iyi[0]))
    r = drc(kart, kok)
    b = pcbnew.LoadBoard(yol)
    kutu = b.GetBoardEdgesBoundingBox()
    ozet = {"kart": kart, "kok": kok, "tohum": en_iyi[1], "puan": en_iyi[0],
            "en": round(pcbnew.ToMM(kutu.GetWidth()) - 0.1, 1), "boy": round(pcbnew.ToMM(kutu.GetHeight()) - 0.1, 1),
            "eleman": len([f for f in b.GetFootprints() if not f.GetReference().startswith("H")]),
            "yol": len([t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]),
            "gecis": len([t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]),
            "ihlal": len(r.get("violations", [])), "baglanmamis": len(r.get("unconnected_items", [])),
            "uyum": len(r.get("schematic_parity", [])),
            "ihlal_turleri": sorted({v["type"] for v in r.get("violations", [])})}
    json.dump(ozet, open(os.path.join(KOK, "out", "pcb", kok + "_sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return r, en_iyi[1]


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[3] == "drc":
        drc(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 3 and sys.argv[3] == "tek":
        pcb_yerlesim.yerlestir(sys.argv[1], sys.argv[2])
        ciz(sys.argv[1], sys.argv[2])
    else:
        otomatik(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 5)
