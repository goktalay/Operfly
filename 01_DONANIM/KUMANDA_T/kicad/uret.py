"""Operfly Pilot T ana kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_T operfly_pilott`.

Kaynak bu dosya ve ortak bölümdür (`10_ORTAK_ARACLAR/kicad/kumanda_ana.py`); `*.kicad_sch` çıktıları elle düzenlenmez.
Pilot T = Pilot 12 ana kartının devresi (batarya, şarj, beslemeler, kumanda radyosu) + telemetri ekranı.
Ekran: EA DOGM128W-6 (128x64, güneşte okunan yarı geçirgen LCD, ST7565R, SPI) + EA LED55X46-A arka ışık (kehribar).
Ekranı giriş kartındaki işlemci sürer: giriş kartının "ekran / genişleme" konnektöründen 10 telli düz kablo gelir.
Ekranın uç sırası ve 9 kondansatörlü tek beslemeli bağlantısı üretici veri sayfasından (DOGM128-6, 01.2026), sembol ve
ayak izi KiCad kütüphanesinden (uç numaraları veri sayfasıyla aynı).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from kart import C0603, Izgara  # noqa: E402
from kumanda_ana import KUTUPHANELER, N7002, SOT23, ana_kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k, kok, sayfalar = ana_kart("operfly_pilott", "Pilot T", "OPFKTL", "KUMANDA_T", BURASI)

ek = Sema(k.P, "Pilot T - telemetri ekrani ve arka isik", kagit="A3", tarih=k.T, ust=kok, ad="Ekran", genel_etiket=True)
kok.alt_sayfa(ek, "ekran.kicad_sch", 177.8, 50.8)
ek.metin("GIRIS KARTINDAN GELEN EKRAN KABLOSU (JST-GH 10, duz kablo): uc sirasi giris kartindaki 'ekran / genisleme' konnektoruyle ayni.", 20, 22)
ek.metin("1 +3V3 (kullanilmaz: ekran bu kartin 3,3 V'undan beslenir), 2 GND, 3 SCK, 4 MOSI, 5 MISO (kullanilmaz: ekran yalniz yazilir),", 20, 28)
ek.metin("6 CS, 7 DC -> A0, 8 RST, 9 BL (arka isik, PWM), 10 GND.", 20, 34)
g = Izgara(40, 75, sutun=9)
k.parca(ek, g, "Connector_Generic_MountingPin:Conn_01x10_MountingPin", "J", "Ekran kablosu (giris karti)", {"Pin_2": "GND", "Pin_3": "DISP_SCK", "Pin_4": "DISP_MOSI",
        "Pin_6": "DISP_CS", "Pin_7": "DISP_DC", "Pin_8": "DISP_RST", "Pin_9": "DISP_BL", "Pin_10": "GND", "MountPin": "GND"},
        "Connector_JST:JST_GH_SM10B-GHS-TB_1x10-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
k.R(ek, g, "33R", "DISP_SCK", "LCD_SCL"); k.R(ek, g, "33R", "DISP_MOSI", "LCD_SI")
k.R(ek, g, "100k", "+3V3", "DISP_CS"); k.R(ek, g, "10k", "DISP_RST", "GND")
k.C(ek, g, "100n", "+3V3"); k.C(ek, g, "1u", "+3V3", fp=C0603)

ek.metin("EKRAN (EA DOGM128W-6, tek besleme 3,3 V): ic gerilim yukseltici 9 adet 1 uF kondansator ister (uretici devresi).", 20, 120)
ek.metin("RST dusukken ekran sifirlamadadir (kablo takili degilken ya da islemci sifirlanirken 10k tutar). Kontrast yazilimla ayarlanir.", 20, 126)
k.koy(ek, "Display_Graphic:EA_DOGM128X-6", "DS", "EA DOGM128W-6 + EA LED55X46-A", 80, 185, {
    "VDD": "+3V3", "VDD2": "+3V3", "VSS": "GND", "SI": "LCD_SI", "SCL": "LCD_SCL", "A0": "DISP_DC", "~{RST}": "DISP_RST", "~{CS1B}": "DISP_CS",
    "V0": "LCD_V0", "V1": "LCD_V1", "V2": "LCD_V2", "V3": "LCD_V3", "V4": "LCD_V4", "VOUT": "LCD_VOUT",
    "CAP1P": "LCD_C1P", "CAP1N": "LCD_C1N", "CAP2P": "LCD_C2P", "CAP2N": "LCD_C2N", "CAP3P": "LCD_C3P",
    "A1+": "BL_A1", "A2+": "BL_A2", "A3+": "BL_A3", "C1-": "BL_K", "C2-": "BL_K", "C3-": "BL_K"}, "Display:EA_DOGM128-6")
g = Izgara(150, 165, sutun=9)
k.C(ek, g, "1u 25V", "LCD_C3P", "LCD_C1N", fp=C0603); k.C(ek, g, "1u 25V", "LCD_C1P", "LCD_C1N", fp=C0603); k.C(ek, g, "1u 25V", "LCD_C2P", "LCD_C2N", fp=C0603)
k.C(ek, g, "1u 25V", "LCD_VOUT", fp=C0603)
for i in range(5):
    k.C(ek, g, "1u 25V", "LCD_V%d" % i, fp=C0603)

ek.metin("ARKA ISIK (kehribar, uc LED yolu, yol basina 82R ile yaklasik 15 mA): 3,3 V'tan dogrudan calisir. DISP_BL = 1 yakar;", 150, 205)
ek.metin("islemci PWM ile kisar. Gunduz kapali kalabilir (ekran arka isiksiz okunur).", 150, 211)
g = Izgara(170, 240, sutun=5)
for i in (1, 2, 3):
    k.R(ek, g, "82R", "+3V3", "BL_A%d" % i)
x, y = g.yer()
k.koy(ek, N7002[0], N7002[1], N7002[2], x, y, {"D": "BL_K", "S": "GND", "G": "DISP_BL"}, SOT23)
k.R(ek, g, "100k", "DISP_BL", "GND")
for ag in ("BL_A1", "BL_A2", "BL_A3", "BL_K"):
    k.bayrak(ek, g, ag)
ek.yaz(os.path.join(BURASI, "ekran.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_pilott.kicad_sch"))
kutuphane_tablolari(BURASI, [kok] + sayfalar + [ek], KUTUPHANELER)
print("yazildi: operfly_pilott (kok + 3 sayfa)")
