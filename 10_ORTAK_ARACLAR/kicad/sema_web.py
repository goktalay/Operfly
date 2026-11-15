"""Kart şematiklerini donanım şeması sayfasında (06_PANELLER/donanim-semasi) gösterilecek biçime çevirir.

Çalıştırma (depo kökünden): python 10_ORTAK_ARACLAR/kicad/sema_web.py [KART ...]
Çıktı: out/sema_web/sema/liste.js (hangi donanımın hangi sayfaları var) ve out/sema_web/sema/<donanım>/<n>.js
(her sayfa: küçültülmüş SVG, betik dosyası içinde). Çıktı depoya eklenmez; sayfa yayımlanırken index.html ile birlikte
yüklenir. Yeni bir kartın şematiği bitince KARTLAR listesine eklenir ve bu betik yeniden çalıştırılır.

SVG küçültme: KiCad yazıları çizgi çizgi çizer ve dosyayı 1 MB'ın üstüne çıkarır; aynı yazı görünmez <text> olarak da
dosyada bulunur. Çizgili yazılar atılır, <text> görünür yapılır (boyut yaklaşık onda bire iner, yazı seçilebilir olur).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CIKTI = os.path.join(KOK, "out", "sema_web", "sema")
# sayfadaki donanım kimliği, kart klasörü, proje kökü, görünen ad
KARTLAR = [
    ("core", "CORE", "operfly_core", "Operfly Core"),
    ("power", "POWER", "operfly_power", "Operfly Power"),
    ("hub", "HUB", "operfly_hub", "Operfly Hub"),
    ("adapter", "PC_ADAPTOR", "operfly_pc_adaptor", "PC adaptörü"),
    ("nav", "NAV", "operfly_nav", "Operfly Nav"),
    ("rx", "RX", "operfly_rx", "Operfly RX"),
    ("radio", "RADIO", "operfly_radio", "Operfly Radio"),
    ("inputs", "KUMANDA_GIRIS", "operfly_kumanda_giris", "Kumanda giriş kartı"),
    ("pilot12", "KUMANDA_12", "operfly_pilot12", "Operfly Pilot 12 ana kartı"),
    ("air", "AIR", "operfly_air", "Operfly Air"),
    ("engine", "ENGINE", "operfly_engine", "Operfly Engine"),
    ("vision", "VISION", "operfly_vision", "Operfly Vision"),
    ("range", "RANGE", "operfly_range", "Operfly Range 10 / 30 / 100"),
    ("cell", "CELL", "operfly_cell", "Operfly Cell"),
    ("pilott", "KUMANDA_T", "operfly_pilott", "Operfly Pilot T"),
    ("pilotpro", "KUMANDA_PRO", "operfly_pilotpro", "Operfly Pilot Pro"),
    ("base", "BASE", "operfly_base", "Operfly Base"),
    ("gr", "YER_RADYO", "operfly_groundradio", "Operfly Ground Radio"),
    ("tracker", "TRACKER", "operfly_tracker", "Operfly Tracker"),
]


def kucult(s):
    """KiCad SVG çıktısını küçültür: çizgili yazıları atar, gizli <text> öğelerini görünür yapar."""
    out, renk, pos = [], "#000000", 0
    tok = re.compile(r'<g class="stroked-text">.*?</g>|<g style="([^"]*)"|<text ([^>]*?)opacity="0" stroke-opacity="0">', re.S)
    for m in tok.finditer(s):
        out.append(s[pos:m.start()])
        pos = m.end()
        t = m.group(0)
        if t.startswith('<g class="stroked-text"'):
            continue
        if t.startswith("<g style"):
            r = re.search(r"stroke:(#[0-9A-Fa-f]{6})", m.group(1))
            if r:
                renk = r.group(1)
            out.append(t)
            continue
        out.append('<text %sfill="%s" stroke="none">' % (m.group(2), renk))
    out.append(s[pos:])
    s = "".join(out)
    s = s[s.index("<svg"):]                                  # XML başlığı ve DOCTYPE sayfaya gömülürken gereksiz
    s = re.sub(r"<title>.*?</title>\s*<desc>.*?</desc>", "", s, count=1, flags=re.S)
    s = re.sub(r"(\d+\.\d{2})\d+", r"\1", s)                 # 0,01 mm çözünürlük yeter
    s = re.sub(r"\n(?=L|\")", " ", s)
    return s.replace("<svg\n", '<svg font-family="Arial, Helvetica, sans-serif"\n', 1)


def sayfalar(kok_dosya):
    """Kök şematikteki alt sayfaları sayfa numarası sırasıyla döndürür: [(sayfa adı, dosya)]."""
    t = open(kok_dosya, encoding="utf-8").read()
    bulunan = re.findall(r'\(property "Sheetname" "([^"]+)".*?\(property "Sheetfile" "([^"]+)".*?\(page "(\d+)"\)', t, re.S)
    return [(ad, dosya) for ad, dosya, _ in sorted(bulunan, key=lambda b: int(b[2]))]


def baslik(dosya):
    m = re.search(r'\(title_block\s*\(title "([^"]*)"', open(dosya, encoding="utf-8").read())
    return m.group(1) if m else ""


def kart(kimlik, klasor, kok, ad):
    dizin = os.path.join(KOK, "01_DONANIM", klasor, "kicad")
    kok_dosya = os.path.join(dizin, kok + ".kicad_sch")
    if not os.path.exists(kok_dosya):
        return None
    hedef = os.path.join(CIKTI, kimlik)
    shutil.rmtree(hedef, ignore_errors=True)
    os.makedirs(hedef)
    liste = []
    with tempfile.TemporaryDirectory() as gecici:
        subprocess.run(["kicad-cli", "sch", "export", "svg", "-o", gecici, kok_dosya], check=True, capture_output=True)
        alt = sayfalar(kok_dosya) or [(None, kok + ".kicad_sch")]
        for i, (sayfa, dosya) in enumerate(alt, 1):
            svg = os.path.join(gecici, kok + ("-" + sayfa if sayfa else "") + ".svg")
            if not os.path.exists(svg):
                raise SystemExit("SVG bulunamadı: %s" % svg)
            govde = kucult(open(svg, encoding="utf-8").read())
            anahtar = "%s/%d" % (kimlik, i)
            with open(os.path.join(hedef, "%d.js" % i), "w", encoding="utf-8", newline="\n") as f:
                f.write("window.OPERFLY_SEMA_YUKLE(%s,%s);\n" % (json.dumps(anahtar), json.dumps(govde, ensure_ascii=False)))
            t = baslik(os.path.join(dizin, dosya))
            liste.append({"ad": sayfa or "Sematik", "baslik": t.split(" - ", 1)[-1] if " - " in t else t, "dosya": "sema/%s/%d.js" % (kimlik, i)})
    return {"ad": ad, "sayfalar": liste}


def main():
    secim = set(a.upper() for a in sys.argv[1:])
    os.makedirs(CIKTI, exist_ok=True)
    eski = {}
    liste_js = os.path.join(CIKTI, "liste.js")
    if os.path.exists(liste_js):
        eski = json.loads(open(liste_js, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sonuc = {}
    for kimlik, klasor, kok, ad in KARTLAR:
        if secim and klasor not in secim and kimlik in eski and os.path.isdir(os.path.join(CIKTI, kimlik)):
            sonuc[kimlik] = eski[kimlik]
            continue
        k = kart(kimlik, klasor, kok, ad)
        if k:
            sonuc[kimlik] = k
            boyut = sum(os.path.getsize(os.path.join(CIKTI, kimlik, f)) for f in os.listdir(os.path.join(CIKTI, kimlik)))
            print("%-10s %2d sayfa, %5d kB" % (klasor, len(k["sayfalar"]), boyut // 1024))
    with open(liste_js, "w", encoding="utf-8", newline="\n") as f:
        f.write("window.OPERFLY_SEMA=" + json.dumps(sonuc, ensure_ascii=False) + ";\n")
    print("yazıldı: %s (%d kart)" % (os.path.relpath(liste_js, KOK), len(sonuc)))


if __name__ == "__main__":
    main()
