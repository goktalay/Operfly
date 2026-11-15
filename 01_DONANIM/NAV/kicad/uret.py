"""Operfly Nav şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py NAV operfly_nav`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + GNSS alıcı modülü (Septentrio mosaic-X5; aynı ayak izine çift antenli mosaic-H de oturur),
anten beslemesi, saniye darbesi (PPS) sürücüsü, servis USB'si, microSD, pusula.
Modülün uç sırası ve çevre devreleri üreticinin donanım kılavuzundandır (mosaic Hardware Manual 1.11.0).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
k = Kart("operfly_nav", "2026-11-15")
kok = Sema(k.P, "Operfly Nav", kagit="A3", tarih=k.T)
kok.metin("Operfly Nav - GNSS karti (OPFNAV)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/NAV/kicad/uret.py.", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA2": "GNSS_RXD1", "PA3": "GNSS_TXD1",              # USART2_TX -> modul RXD1, USART2_RX <- modul TXD1 (COM1: olcum ve komut)
      "PA1": "GNSS_CTS1", "PA0": "GNSS_RTS1",              # USART2_RTS -> modul CTS1, USART2_CTS <- modul RTS1
      "PB6": "GNSS_RXD2", "PB7": "GNSS_TXD2",              # USART1_TX -> modul RXD2, USART1_RX <- modul TXD2 (COM2: RTK duzeltmeleri)
      "PB3": "GNSS_PPS",                                   # TIM2_CH2: alicinin kendi saniye darbesi (omurga darbesi PA15, TIM2_CH1)
      "PB4": "PPS_OE_N",                                   # 0: saniye darbesi omurgaya surulur
      "PB0": "GNSS_NRST", "PB1": "GNSS_RDY",
      "PA4": "ANT_BIAS_EN",                                # 1: antene 3,3 V besleme verilir
      "PA8": "GNSS_EVENT",                                 # TIM1_CH1: aliciya olay isareti (ornegin kamera tetigi)
      "PC6": "GNSS_LOGBTN", "PC7": "GNSS_LOGLED",
      "PB10": "MAG_SCL", "PB11": "MAG_SDA", "PA6": "MAG_DRDY", "PA7": "MAG_RST_N"}   # I2C2
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, pps=True, ldo33=False)

# --- GNSS: alıcı modülü, besleme, antenler, saniye darbesi -------------------
gn = Sema(k.P, "Operfly Nav - GNSS alicisi, besleme, antenler, saniye darbesi", kagit="A1", tarih=k.T, ust=kok, ad="GNSS", genel_etiket=True)
kok.alt_sayfa(gn, "gnss.kicad_sch", 101.6, 50.8)
gn.metin("GNSS ALICISI (Septentrio mosaic-X5; ayni ayak izine cift antenli mosaic-H oturur). Uc sirasi uretici belgesinden (Ek G).", 30, 28)
gn.metin("Uretici kurallari: SYNC = 1V8_OUT; ic saat icin REF_I = REF_O ve 2V8_IN = 2V8_OUT; RTC_XTALI ve AB7 topraga; VDD_BAT = VDD_3V3;", 30, 34)
gn.metin("kullanilmayan uclar (Ethernet, COM4, ONOFF, GP1/GP2, EVENTB, VTUNE...) bos birakilir. Sag kutu: ayrilmis uclar, hepsi bos.", 30, 40)
k.koy(gn, "operfly:mosaic-X5", "U", "mosaic-X5 (secenek: mosaic-H)", 110, 150, {
    "VDD_3V3": "+3V3", "VDD_BAT": "+3V3", "GND": "GND", "Reserved_GND": "GND", "RTC_XTALI": "GND",
    "VANT": "+VANT", "1V8_OUT": "+1V8_GNSS", "SYNC": "+1V8_GNSS", "2V8_OUT": "GNSS_2V8", "2V8_IN": "GNSS_2V8",
    "REF_O": "GNSS_REF", "REF_I": "GNSS_REF", "ANT_1": "GNSS_ANT1", "ANT_2": "GNSS_ANT2",
    "nRST_IN": "GNSS_NRST", "MODULE_RDY": "GNSS_RDY",
    "TXD1": "GNSS_TXD1", "RXD1": "GNSS_RXD1", "RTS1": "GNSS_RTS1", "CTS1": "GNSS_CTS1", "TXD2": "GNSS_TXD2", "RXD2": "GNSS_RXD2",
    "TXD3": "GNSS_TXD3", "RXD3": "GNSS_RXD3",
    "PPSO": "GNSS_PPSO", "EVENTA": "GNSS_EVENTA", "GPLED": "GNSS_GPLED", "LOGLED": "GNSS_LOGLED", "LOGBUTTON": "GNSS_LOGBTN",
    "USB_VBUS1": "VBUS_USB", "USB_DEV_P": "USB_DP", "USB_DEV_N": "USB_DM",
    "SD1_CLK": "SD_CLK", "SD1_CMD": "SD_CMD", "SD1_DATA0": "SD_DAT0"},
    "operfly_ayak:Septentrio_mosaic_LGA-239_31x31mm_P1.27mm")
g = Izgara(50, 300, sutun=12)
k.C(gn, g, "22u 6V3", "+3V3", fp=C0805); k.C(gn, g, "100n", "+3V3"); k.C(gn, g, "100n", "+3V3"); k.C(gn, g, "100n", "+1V8_GNSS")
for ag in ("GNSS_TXD1", "GNSS_RXD1", "GNSS_TXD3", "GNSS_RXD3", "GNSS_NRST", "GNSS_PPS"):
    k.olcum_noktasi(gn, g, ag)

gn.metin("3,3 V BESLEME (AP7361C, 1 A): alici en cok 0,5 A ceker (uretici: besleme en az 0,5 A verebilmeli). Dugum islemcisi de bu raydadir;", 290, 28)
gn.metin("boylece islemci, alici beslemesizken girislerini suremez. Isi: (5 - 3,3) V x 0,35 A = 0,6 W; kilif altina genis bakir gerekir.", 290, 34)
g = Izgara(310, 70, sutun=12)
k.parca(gn, g, "Regulator_Linear:AP7361C-33E", "U", "AP7361C-33E", {"VI": "+5V", "GND": "GND", "VO": "+3V3"}, "Package_TO_SOT_SMD:SOT-223-3_TabPin2")
k.C(gn, g, "10u 10V", "+5V", fp=C0805); k.C(gn, g, "10u 10V", "+3V3", fp=C0805); k.C(gn, g, "100n", "+3V3")

gn.metin("ANTEN BESLEMESI (+VANT, 3,3 V): ayri, gurultusuz regulator; islemci acar. Sifirlamada kapalidir: anten ucuna dogru gerilim cikmaz.", 290, 110)
gn.metin("Alici bu gerilimi ANT_1 ucundan antene verir, 150 mA'da sinirlar ve kisa devrede keser (dis besleme devresi gerekmez).", 290, 116)
g = Izgara(310, 150, sutun=12)
k.parca(gn, g, "Regulator_Linear:LP5907MFX-3.3", "U", "LP5907MFX-3.3", {"IN": "+5V", "EN": "ANT_BIAS_EN", "GND": "GND", "OUT": "+VANT"}, "Package_TO_SOT_SMD:SOT-23-5")
k.C(gn, g, "1u", "+5V"); k.C(gn, g, "1u", "+VANT"); k.R(gn, g, "100k", "ANT_BIAS_EN", "GND")

gn.metin("ANTENLER: ana anten dogrudan ANT_1'e (koruma ve besleme alicinin icinde). Ikinci anten yalnizca mosaic-H ile kullanilir.", 290, 195)
gn.metin("mosaic-X5 dizgisi: ANT_2 0R ile topraga, ikinci anten yolu DNP. mosaic-H dizgisi: topraklama 0R'si DNP, yol elemanlari dizilir", 290, 201)
gn.metin("(uretici devresi: iki bobin (Wurth 744786139A) + 100 pF ile besleme ana hattan ikinci antene tasinir, ikinci hatta koruma diyotu).", 290, 207)
g = Izgara(310, 245, sutun=12)
SMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
x, y = g.yer(); g.yer()
k.koy(gn, "Connector:Conn_Coaxial", "J", "ANT 1 (SMA)", x + 5, y, {"In": "GNSS_ANT1", "Ext": "GND"}, SMA)
x, y = g.yer(); g.yer()
k.koy(gn, "Connector:Conn_Coaxial", "J", "ANT 2 (SMA)", x + 5, y, {"In": "ANT2_RF", "Ext": "GND"}, SMA)
k.R(gn, g, "0R", "GNSS_ANT2", "GND")
k.R(gn, g, "0R", "GNSS_ANT2", "ANT2_RF", dnp=True)
k.iki(gn, g, "Device:L", "L", "39n 0603", "GNSS_ANT1", "ANT_BIAS_MID", "Inductor_SMD:L_0603_1608Metric", dnp=True)
k.iki(gn, g, "Device:L", "L", "39n 0603", "ANT_BIAS_MID", "ANT2_RF", "Inductor_SMD:L_0603_1608Metric", dnp=True)
k.C(gn, g, "100p", "ANT_BIAS_MID", dnp=True)
k.iki(gn, g, "Device:D_TVS", "D", "SESD0402X1BN", "ANT2_RF", "GND", "Diode_SMD:D_0402_1005Metric", dnp=True)

gn.metin("SANIYE DARBESI: alici cikisi 1,8 V'tur ve acilista kisa sure belirsizdir. Seviye cevirici 3,3 V'a cikarir (GNSS_PPS, islemciye);", 290, 300)
gn.metin("uc durumlu tampon darbeyi omurgaya surer. Tampon sifirlamada kapalidir; islemci ancak zaman gecerliyken acar.", 290, 306)
gn.metin("Boylece ayni omurgada iki Nav karti bulunsa da hatti yalnizca secilen kart surer.", 290, 312)
g = Izgara(310, 350, sutun=12)
x, y = g.yer(); g.yer()
k.koy(gn, "Logic_LevelTranslator:SN74LVC1T45DBV", "U", "SN74LVC1T45DBV", x + 12, y, {
    "VCCA": "+1V8_GNSS", "VCCB": "+3V3", "GND": "GND", "A": "GNSS_PPSO", "B": "GNSS_PPS", "DIR": "+1V8_GNSS"}, "Package_TO_SOT_SMD:SOT-23-6")
k.R(gn, g, "10k", "GNSS_PPSO", "GND"); k.R(gn, g, "10k", "GNSS_PPS", "GND"); k.C(gn, g, "100n", "+3V3")
x, y = g.yer(); g.yer()
k.koy(gn, "74xGxx:74LVC1G125", "U", "74LVC1G125", x + 15, y, {"1": "PPS_OE_N", "2": "GNSS_PPS", "4": "PPS_DRV", "5": "+3V3", "3": "GND"}, "Package_TO_SOT_SMD:SOT-353_SC-70-5")
k.R(gn, g, "10k", "+3V3", "PPS_OE_N"); k.R(gn, g, "33R", "PPS_DRV", "PPS_BUS"); k.C(gn, g, "100n", "+3V3")

gn.metin("OLAY GIRISI: islemci aliciya zaman isareti verir (1,8 V giris; 10 k / 12 k bolucu 3,3 V'u 1,8 V'a indirir).", 290, 400)
g = Izgara(310, 430, sutun=12)
k.R(gn, g, "10k", "GNSS_EVENT", "GNSS_EVENTA"); k.R(gn, g, "12k", "GNSS_EVENTA", "GND")
gn.yaz(os.path.join(BURASI, "gnss.kicad_sch"))

# --- Çevre: servis USB'si, microSD, pusula, durum ışıkları --------------------
cv = Sema(k.P, "Operfly Nav - servis USB, microSD, pusula, durum isiklari", kagit="A2", tarih=k.T, ust=kok, ad="Cevre", genel_etiket=True)
kok.alt_sayfa(cv, "cevre.kicad_sch", 177.8, 50.8)
cv.metin("SERVIS USB'si (Type-C, yalnizca veri): alicinin ayar arayuzu ve yazilim guncellemesi icin. Karti beslemez;", 30, 28)
cv.metin("VBUS yalnizca alicinin USB katini besler (en cok 50 mA). Devre ureticinin ornegidir: konnektor - koruma - alici.", 30, 34)
g = Izgara(50, 80, sutun=10)
k.parca(cv, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C", {"VBUS": "VBUS_USB", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2",
        "D+": "USB_DP", "D-": "USB_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
k.koy(cv, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "5": "VBUS_USB", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
k.R(cv, g, "5k1", "USB_CC1", "GND"); k.R(cv, g, "5k1", "USB_CC2", "GND"); k.C(cv, g, "1u 16V", "VBUS_USB", fp=C0603)

cv.metin("microSD (ham olcum kaydi, sonradan hassas konum hesabi icin): alici 1 bit kipte surer. Devre ureticinin ornegidir:", 30, 150)
cv.metin("DAT3 33 k ile yukari cekili, DAT1/DAT2 bos, hatlarda koruma diyotlari. Kart algilama anahtari kullanilmaz.", 30, 156)
g = Izgara(50, 200, sutun=10)
k.parca(cv, g, "Connector:Micro_SD_Card_Det_Hirose_DM3AT", "J", "microSD DM3AT-SF-PEJM5", {
    "DAT0": "SD_DAT0", "DAT3/CD": "SD_DAT3", "CMD": "SD_CMD", "CLK": "SD_CLK", "VDD": "+3V3", "VSS": "GND", "SHIELD": "GND"},
    "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5", bosluk=3, dx=35)
k.R(cv, g, "33k", "+3V3", "SD_DAT3"); k.C(cv, g, "10u", "+3V3", fp=C0805); k.C(cv, g, "100n", "+3V3")
for ag in ("SD_CLK", "SD_CMD", "SD_DAT0"):
    k.iki(cv, g, "Device:D_TVS", "D", "ESD 0402 (<=5 pF)", ag, "GND", "Diode_SMD:D_0402_1005Metric")

cv.metin("PUSULA (IST8310, I2C2; adres uclari toprakta): GNSS karti guc kablolarindan uzakta durdugu icin pusula burada daha temiz olcer.", 300, 28)
g = Izgara(320, 80, sutun=10)
x, y = g.yer(); g.yer(); g.yer()
k.koy(cv, "Sensor_Magnetic:IST8310", "U", "IST8310", x + 20, y, {"SCL": "MAG_SCL", "SDA": "MAG_SDA", "AVDD": "+3V3", "DVDD": "+3V3",
      "VSS": "GND", "C1": "MAG_C1", "~{RST}": "MAG_RST_N", "DRDY": "MAG_DRDY", "CAD0": "GND", "CAD1": "GND"}, "Package_LGA:LGA-16_3x3mm_P0.5mm")
k.C(cv, g, "4u7", "MAG_C1", fp=C0603); k.C(cv, g, "100n", "+3V3"); k.C(cv, g, "100n", "+3V3")
k.R(cv, g, "2k2", "+3V3", "MAG_SCL"); k.R(cv, g, "2k2", "+3V3", "MAG_SDA"); k.R(cv, g, "10k", "+3V3", "MAG_RST_N")

cv.metin("DURUM ISIKLARI: alici cikislari (en cok 10 mA) 1 k ile dogrudan surer; 10 k asagi cekme acilista sonuk tutar.", 300, 150)
g = Izgara(320, 200, sutun=10)
for ag, renk in (("GNSS_GPLED", "yesil (konum)"), ("GNSS_LOGLED", "sari (kayit)")):
    k.R(cv, g, "1k", ag, ag + "_A"); k.iki(cv, g, "Device:LED", "D", "LED " + renk, "GND", ag + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(cv, g, "10k", ag, "GND")
cv.yaz(os.path.join(BURASI, "cevre.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_nav.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gn, cv], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_nav (kok + 3 sayfa)")
