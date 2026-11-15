"""Otomatik çizilen kartın sonucunu belgeye işler: pcb_ayar.py'ye tohumu ve kart ölçüsünü yazar, README'ye
"Kart çizimi" bölümünü ekler (varsa yeniler), üstten görüntüsünü `out/pcb/gor/<kök>.png` olarak üretir.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/pcb_rapor.py <KART> <kök> ["karta özel not" ...]`
Önce `pcb_ciz.py` çalıştırılmış olmalıdır (`out/pcb/<kök>_sonuc.json`).
"""
import json
import os
import re
import subprocess
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASLIK = "## Kart çizimi"
GENEL = [
    "Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.",
    "Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.",
    "Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.",
    "Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.",
    "Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.",
    "Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.",
    "Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.",
]


def rapor(kart, kok, notlar):
    s = json.load(open(os.path.join(KOK, "out", "pcb", kok + "_sonuc.json"), encoding="utf-8"))
    klasor = os.path.join(KOK, "01_DONANIM", kart)
    # pcb_ayar.py
    ayar_yolu = os.path.join(klasor, "kicad", "pcb_ayar.py")
    if os.path.exists(ayar_yolu):
        t = open(ayar_yolu, encoding="utf-8").read()
        if re.search(r'"tohum":\s*\d+', t):
            t = re.sub(r'"tohum":\s*\d+', '"tohum": %d' % s["tohum"], t)
        else:
            t = t.replace("AYAR = {\n", 'AYAR = {\n    "tohum": %d,\n' % s["tohum"], 1)
        if '"en"' not in t:
            t = t.replace("AYAR = {\n", 'AYAR = {\n    "en": %.1f, "boy": %.1f,\n' % (s["en"], s["boy"]), 1)
    else:
        t = ('"""Kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""\n'
             'AYAR = {\n    "en": %.1f, "boy": %.1f,\n    "tohum": %d,\n}\n' % (s["en"], s["boy"], s["tohum"]))
    open(ayar_yolu, "w", encoding="utf-8", newline="\n").write(t)
    # README bölümü
    temiz = s["ihlal"] == 0 and s["baglanmamis"] == 0
    b = BASLIK + " (otomatik)\n\n"
    b += ("Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle\n"
          "(`pcb_ciz.py`). Dosya: `kicad/%s.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.\n"
          "Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py %s %s`.\n\n" % (kok, kart, kok))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import pcb_yerlesim
    ayar = pcb_yerlesim.ayar_oku(kart)
    if ayar["katman"] == 4:
        dizilim = "4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal)"
    else:
        dizilim = "%d katman (%s; diğer katmanlar sinyal, elemanlar üstte)" % (ayar["katman"], ", ".join("%s: %s" % (k.replace("In", "iç ").replace(".Cu", ""), v.replace("GND", "toprak")) for k, v in sorted(ayar["duzlemler"].items())))
    b += "- **Kart:** %.0f x %.0f mm, %s, %d eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.\n" % (s["en"], s["boy"], dizilim, s["eleman"])
    b += "- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.\n"
    if temiz:
        b += "- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç%s. %d yol parçası, %d geçiş.\n" % ("; şematik-kart uyumu temiz" if s["uyum"] == 0 else "; şematik-kart uyum uyarısı %d" % s["uyum"], s["yol"], s["gecis"])
    else:
        b += ("- **Denetim: KART TAMAMLANMADI.** DRC %d ihlal (%s), %d bağlanmamış uç. Otomatik yol çizici bu kartı bitiremedi;\n"
              "  kalan bağlantılar elle çizilmeli ya da yerleşim elle düzeltilip yeniden denenmeli.\n" % (s["ihlal"], ", ".join(s["ihlal_turleri"]) or "-", s["baglanmamis"]))
    b += "\n**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:\n\n"
    for n in list(notlar) + GENEL:
        b += "- %s\n" % n
    yol = os.path.join(klasor, "README.md")
    t = open(yol, encoding="utf-8").read().rstrip("\n")
    i = t.find("\n" + BASLIK)
    if i >= 0:
        t = t[:i].rstrip("\n")
    open(yol, "w", encoding="utf-8", newline="\n").write(t + "\n\n" + b)
    # Görüntü
    cikti = os.path.join(KOK, "out", "pcb", "gor", kok + ".png")
    os.makedirs(os.path.dirname(cikti), exist_ok=True)
    subprocess.run(["kicad-cli", "pcb", "render", "--side", "top", "-w", "1600", "-h", "1200", "-o", cikti,
                    os.path.join(klasor, "kicad", kok + ".kicad_pcb")], capture_output=True)
    print("%s: %.0f x %.0f mm, %d eleman, %d yol, %d geçiş, DRC %d ihlal / %d bağlanmamış, tohum %d -> %s"
          % (kart, s["en"], s["boy"], s["eleman"], s["yol"], s["gecis"], s["ihlal"], s["baglanmamis"], s["tohum"], "TEMİZ" if temiz else "TAMAMLANMADI"))


if __name__ == "__main__":
    rapor(sys.argv[1], sys.argv[2], sys.argv[3:])
