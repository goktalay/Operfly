"""Operfly kumanda giriş kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_GIRIS operfly_kumanda_giris`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Kart üç kumandada (Pilot 12, Pilot T, Pilot Pro) ortaktır ve kumandanın gerçek zamanlı işlemcisini taşır:
çubukları ve anahtarları okur, kumanda paketini şifreler, kumanda radyosunu ana kart üzerinden doğrudan sürer.
Ana kartla bağlantı: 13_DOKUMANTASYON/KUMANDA_ARAYUZU.md (20 kontaklı yassı kablo).
Omurgaya bağlanan bir kart değildir; ortak düğüm devresi (CAN, 12 V) kullanılmaz.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from kart import C0603, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
FB0603 = "Inductor_SMD:L_0603_1608Metric"
GH = "Connector_JST:JST_GH_SM%02dB-GHS-TB_1x%02d-1MP_P1.25mm_Horizontal"
k = Kart("operfly_kumanda_giris", "2026-11-15")
kok = Sema(k.P, "Operfly kumanda giris karti", kagit="A3", tarih=k.T)
kok.metin("Operfly kumanda giris karti (Pilot 12, Pilot T ve Pilot Pro'da ortak)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/KUMANDA_GIRIS/kicad/uret.py.", 25.4, 33.02, 1.6)


def gh(sema, g, n, deger, aglar, bosluk=1):
    """JST-GH konnektörü, n kontak; tutturma pedleri toprağa."""
    ag = {"Pin_%d" % (i + 1): a for i, a in enumerate(aglar)}
    ag["MountPin"] = "GND"
    return k.parca(sema, g, "Connector_Generic_MountingPin:Conn_01x%02d_MountingPin" % n, "J", deger, ag, GH % (n, n), bosluk=bosluk, dx=8)


# İşlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
PINLER = {
    "PA0": "GIM_L_X", "PA1": "GIM_L_Y", "PA2": "GIM_R_X", "PA3": "GIM_R_Y",        # ADC1_IN0..3
    "PA4": "WHEEL_L", "PA5": "WHEEL_R",                                            # ADC1_IN4, IN5
    "PA6": "SW_A", "PA7": "SW_B", "PB0": "SW_C", "PB1": "SW_D", "PB2": "SW_E", "PB10": "SW_F",   # ADC1_IN6..11
    "PB11": "NAV_ADC",                                                             # ADC1_IN15
    "PB6": "RADIO_RXD", "PB7": "RADIO_TXD",                                        # USART1_TX -> radyo RX, USART1_RX <- radyo TX
    "PB3": "RADIO_CTS", "PB4": "RADIO_RTS",                                        # USART1_RTS -> radyo CTS, USART1_CTS <- radyo RTS
    "PA9/PA11": "USB_DM", "PA10/PA12": "USB_DP",                                   # USB (PA11 = D-, PA12 = D+)
    "PB8": "I2C_SCL", "PB9": "I2C_SDA", "PB5": "SE_ENA",                           # I2C1: guvenli eleman + ana kart
    "PB13": "DISP_SCK", "PB14": "DISP_MISO", "PB15": "DISP_MOSI",                  # SPI2
    "PA15": "DISP_CS", "PC6": "DISP_DC", "PC7": "DISP_RST", "PA8": "DISP_BL",      # PA8 = TIM1_CH1
    "PD0": "RADIO_OFF", "PD1": "RADIO_BOOT_N", "PD2": "PWR_HOLD", "PD3": "PWR_BTN_N", "PC13": "ALERT_N",
    "PC14": "BTN_1", "PC15": "BTN_2",
    "PA9/UCPD1_DBCC1": "BUZZER",                                                   # TIM1_CH2
    "PA10/UCPD1_DBCC2": "LED_DURUM", "PB12": "LED_UYARI",
    "PA13": "SWDIO", "PA14": "SWCLK", "PF0": "HSE_IN", "PF1": "HSE_OUT", "PF2": "NRST",
    "VDD": "+3V3", "VBAT": "+3V3", "VREF+": "+3V3A", "VSS": "GND",
}

# --- İşlemci, güvenli eleman, ana kart ve ekran bağlantıları ------------------
ic = Sema(k.P, "Kumanda giris karti - islemci, guvenli eleman, ana kart ve ekran baglantilari", kagit="A1", tarih=k.T, ust=kok, ad="Islemci", genel_etiket=True)
kok.alt_sayfa(ic, "islemci.kicad_sch", 25.4, 50.8)
ic.metin("ISLEMCI (STM32G0B1CET6): cubuklari ve anahtarlari okur, kumanda paketini sifreler, kumanda radyosunu dogrudan surer.", 30, 28)
ic.metin("Boylece kumanda yolu, ust modeldeki Jetson'a ya da ekrana bagli degildir. 14 analog giristen 13'u kullanilir.", 30, 34)
lid = k.lib(ic, "MCU_ST_STM32G0:STM32G0B1CETx")
eksik = set(PINLER) - {ad for _no, ad, _x, _y, _a in ic.pinler[lid]}
assert not eksik, eksik
k.koy(ic, lid, "U", "STM32G0B1CET6", 110, 130, PINLER, "Package_QFP:LQFP-48_7x7mm_P0.5mm")
g = Izgara(200, 80, sutun=10)
for deger in ("4u7", "100n", "100n"):
    k.C(ic, g, deger, "+3V3", fp=C0603 if deger == "4u7" else "Capacitor_SMD:C_0402_1005Metric")
k.koy(ic, "Device:Crystal_GND24", "Y", "16 MHz", *g.yer(), {"1": "HSE_IN", "3": "HSE_OUT", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(ic, g, "10p", "HSE_IN"); k.C(ic, g, "10p", "HSE_OUT")
k.R(ic, g, "10k", "+3V3", "NRST"); k.C(ic, g, "100n", "NRST")
g.satir()
for a in ("SWDIO", "SWCLK", "NRST"):
    k.olcum_noktasi(ic, g, a)
for ag, ad in (("LED_DURUM", "yesil"), ("LED_UYARI", "kirmizi")):
    k.iki(ic, g, "Device:LED", "D", "LED " + ad, ag, ag + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(ic, g, "1k", "+3V3", ag + "_A")

ic.metin("ANALOG BESLEME (+3V3A): ferrit + kondansator. Islemcinin olcum referansi ve cubuklarin beslemesi ayni raydadir;", 30, 215)
ic.metin("olcum oransal oldugu icin besleme dalgalanmasi sonucu etkilemez.", 30, 221)
g = Izgara(50, 250, sutun=10)
k.iki(ic, g, "Device:FerriteBead", "FB", "BLM18PG221", "+3V3", "+3V3A", FB0603)
k.C(ic, g, "4u7", "+3V3A", fp=C0603); k.C(ic, g, "1u", "+3V3A"); k.C(ic, g, "100n", "+3V3A")
for ag in ("+3V3", "+3V3A", "GND"):
    k.bayrak(ic, g, ag)

ic.metin("GUVENLI ELEMAN (SE050): kumandanin kimligi ve anahtarlari islemcinin yaninda durur. I2C yukari cekmeleri bu karttadir.", 30, 300)
g = Izgara(50, 340, sutun=10)
x0, y0 = g.yer(); g.yer(); g.yer()
k.koy(ic, "operfly:SE050", "U", "SE050E2HQ1", x0 + 20, y0, {"I2C_SDA": "I2C_SDA", "I2C_SCL": "I2C_SCL", "ENA": "SE_ENA",
      "VIN": "+3V3", "VCC": "SE_VCC", "VOUT": "SE_VCC", "VSS": "GND", "EP": "GND"}, "Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm")
k.R(ic, g, "2k2", "+3V3", "I2C_SCL"); k.R(ic, g, "2k2", "+3V3", "I2C_SDA"); k.R(ic, g, "10k", "+3V3", "SE_ENA")
k.C(ic, g, "100n", "+3V3"); k.C(ic, g, "2u2", "SE_VCC", fp=C0603)

ic.metin("ANA KART BAGLANTISI (20 kontakli yassi kablo, 0,5 mm): besleme ana karttan gelir. Uc sirasi: 13_DOKUMANTASYON/KUMANDA_ARAYUZU.md.", 330, 28)
ic.metin("Radyo hatlari ana karttaki kumanda radyosuna, USB ana karttaki Type-C konnektore, I2C batarya olcere gider.", 330, 34)
ANA = ["GND", "+3V3", "+3V3", "GND", "RADIO_RXD", "RADIO_TXD", "RADIO_CTS", "RADIO_RTS", "RADIO_OFF", "RADIO_BOOT_N",
       "GND", "USB_DM", "USB_DP", "GND", "I2C_SCL", "I2C_SDA", "ALERT_N", "PWR_BTN_N", "PWR_HOLD", "BUZZER"]
ag = {"Pin_%d" % (i + 1): a for i, a in enumerate(ANA)}
ag["MountPin"] = "GND"
k.koy(ic, "Connector_Generic_MountingPin:Conn_01x20_MountingPin", "J", "Ana kart (FFC 20)", 360, 100, ag,
      "Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
g = Izgara(420, 80, sutun=8)
k.R(ic, g, "100k", "RADIO_OFF", "GND"); k.R(ic, g, "10k", "+3V3", "RADIO_BOOT_N"); k.R(ic, g, "10k", "+3V3", "ALERT_N")
k.R(ic, g, "100k", "+3V3", "PWR_BTN_N"); k.R(ic, g, "100k", "PWR_HOLD", "GND"); k.R(ic, g, "100k", "BUZZER", "GND")
k.C(ic, g, "10u", "+3V3", fp="Capacitor_SMD:C_0805_2012Metric")

ic.metin("EKRAN / GENISLEME (10 kontak): Pilot T'nin kucuk ekrani icin SPI + denetim hatlari. Pilot 12'de bos kalir.", 330, 200)
g = Izgara(350, 240, sutun=8)
gh(ic, g, 10, "Ekran / genisleme", ["+3V3", "GND", "DISP_SCK", "DISP_MOSI", "DISP_MISO", "DISP_CS", "DISP_DC", "DISP_RST", "DISP_BL", "GND"], bosluk=2)
k.R(ic, g, "10k", "+3V3", "DISP_CS"); k.R(ic, g, "100k", "DISP_BL", "GND")
ic.yaz(os.path.join(BURASI, "islemci.kicad_sch"))

# --- Girişler: çubuklar, tekerlekler, anahtarlar, yön tuşu, düğmeler ----------
gr = Sema(k.P, "Kumanda giris karti - cubuklar, tekerlekler, anahtarlar, dugmeler", kagit="A1", tarih=k.T, ust=kok, ad="Girisler", genel_etiket=True)
kok.alt_sayfa(gr, "girisler.kicad_sch", 101.6, 50.8)
gr.metin("CUBUKLAR (Hall etkili gimbal, 3,3 V, eksen basina analog cikis): 4 kontak = +3V3A, X, Y, GND (bizim tanimimiz).", 30, 28)
gr.metin("Secilen gimbalin kendi kablosu bu siraya gore uyarlanir. Her giriste 1 k + 100 nF: suzme ve asiri gerilimde akim sinirlama.", 30, 34)
g = Izgara(50, 70, sutun=12)
for yan in ("L", "R"):
    gh(gr, g, 4, "Cubuk %s" % ("sol" if yan == "L" else "sag"), ["+3V3A", "GIM_%s_X_J" % yan, "GIM_%s_Y_J" % yan, "GND"])
    for e in ("X", "Y"):
        k.R(gr, g, "1k", "GIM_%s_%s_J" % (yan, e), "GIM_%s_%s" % (yan, e)); k.C(gr, g, "100n", "GIM_%s_%s" % (yan, e))
k.C(gr, g, "100n", "+3V3A")

gr.metin("TEKERLEKLER (potansiyometre ya da Hall, analog): 3 kontak = +3V3A, sinyal, GND.", 30, 120)
g = Izgara(50, 150, sutun=12)
for yan in ("L", "R"):
    gh(gr, g, 3, "Tekerlek %s" % ("sol" if yan == "L" else "sag"), ["+3V3A", "WHEEL_%s_J" % yan, "GND"])
    k.R(gr, g, "1k", "WHEEL_%s_J" % yan, "WHEEL_%s" % yan); k.C(gr, g, "100n", "WHEEL_%s" % yan); k.R(gr, g, "1M", "WHEEL_%s" % yan, "GND")

gr.metin("ANAHTARLAR A-F (2 ya da 3 konumlu): 3 kontak = +3V3A, ortak uc, GND. Anahtar ortak ucu +3V3A'ya ya da GND'ye baglar;", 30, 200)
gr.metin("orta konumda iki 47 k giris gerilimini yariya ceker. Tek analog giris uc konumu okur; kopuk kablo da 'orta' gorunur (ariza anlasilir).", 30, 206)
g = Izgara(50, 240, sutun=12)
for i, h in enumerate("ABCDEF"):
    gh(gr, g, 3, "Anahtar %s" % h, ["+3V3A", "SW_%s_J" % h, "GND"])
    k.R(gr, g, "47k", "+3V3A", "SW_%s_J" % h); k.R(gr, g, "47k", "SW_%s_J" % h, "GND")
    k.R(gr, g, "1k", "SW_%s_J" % h, "SW_%s" % h); k.C(gr, g, "100n", "SW_%s" % h)
    if i % 2 == 1:
        g.satir()

gr.metin("YON TUSU (5 yonlu, menu icin): 6 kontak = GND, orta, yukari, asagi, sol, sag. Her yon farkli direncle tek analog girise baglanir:", 30, 340)
gr.metin("bos 3,3 V; orta 0 V; yukari 0,60 V; asagi 1,06 V; sol 1,65 V; sag 2,27 V (10 k yukari cekme ile).", 30, 346)
g = Izgara(50, 380, sutun=12)
gh(gr, g, 6, "Yon tusu", ["GND", "NAV_C", "NAV_U", "NAV_D", "NAV_L", "NAV_R"], bosluk=2)
k.R(gr, g, "10k", "+3V3A", "NAV_ADC"); k.C(gr, g, "100n", "NAV_ADC")
for ag, deger in (("NAV_C", "0R"), ("NAV_U", "2k2"), ("NAV_D", "4k7"), ("NAV_L", "10k"), ("NAV_R", "22k")):
    k.R(gr, g, deger, ag, "NAV_ADC")

gr.metin("DUGMELER (anlik basmali, 2 adet): 2 kontak = sinyal, GND. 10 k yukari cekme, 100 nF.", 30, 430)
g = Izgara(50, 460, sutun=12)
for i in (1, 2):
    gh(gr, g, 2, "Dugme %d" % i, ["BTN_%d_J" % i, "GND"])
    k.R(gr, g, "10k", "+3V3", "BTN_%d" % i); k.R(gr, g, "1k", "BTN_%d_J" % i, "BTN_%d" % i); k.C(gr, g, "100n", "BTN_%d" % i)
gr.yaz(os.path.join(BURASI, "girisler.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_kumanda_giris.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, ic, gr], {"operfly": ORTAK_URI})
print("yazildi: operfly_kumanda_giris (kok + 2 sayfa)")
