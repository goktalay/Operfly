"""Operfly Pilot Pro ana kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_PRO operfly_pilotpro`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
1. ADIM (bu dosyanın şimdiki kapsamı): güç işlemcisi (düğüm devresi), USB Type-C güç anlaşması, 4 hücreli batarya şarjı
ve güç yolu, 3,3 V ve 5 V, güç düğmesi, kumanda radyosu ve giriş kartı bağlantısı. Bu kadarıyla kart kumanda olarak çalışır.
2. ADIM (henüz çizilmedi): Jetson çekirdeği, NVMe, Ethernet, geniş bant radyo, ekran ve USB göbeği (README'de liste).

Devre değerleri üretici belgelerindendir: BQ25798 (SLUSDV2C: uç açıklamaları, Tablo 7-1, bölüm 7.3.9.5, 7.3.12, 8.2),
STUSB4500 (DS12499 Rev 3, Şekil 10 "Typical schematic with MCU"), AP6320x (düğüm ve RX kartındaki devreler),
RFD900ux (V1.3; RX kartındaki bağlantı).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C1206, ORTAK_URI, XAL, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
N7002 = ("Transistor_FET:2N7002", "Q", "2N7002")
SOT23 = "Package_TO_SOT_SMD:SOT-23"
TSOT6 = "Package_TO_SOT_SMD:TSOT-23-6"
TVS25 = ("Device:D_TVS", "D", "ESDA25P35-1U1M")
TVS25_FP = "Diode_SMD:D_0603_1608Metric"

k = Kart("operfly_pilotpro", "2026-11-15")
kok = Sema(k.P, "Operfly Pilot Pro", kagit="A3", tarih=k.T)
kok.metin("Operfly Pilot Pro - kumanda ana karti (OPFKPR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/KUMANDA_PRO/kicad/uret.py. 1. adim: guc ve kumanda yolu. Jetson, ekran ve genis bant radyo 2. adimda.", 25.4, 33.02, 1.6)

EK = {"PB10": "PWR_SCL", "PB11": "PWR_SDA",      # I2C2: sarj entegresi, guc anlasmasi entegresi, bataryanin kendi olceri
      "PB3": "I2C_SCL", "PB4": "I2C_SDA",        # I2C3 (kole): giris kartindaki kumanda islemcisiyle dogrudan baglanti
      "PA0": "CHG_INT_N", "PA1": "PD_ALERT_N",   # kesme girisleri
      "PA4": "PWR_BTN_M",                        # guc dugmesi (0 = basili)
      "PA5": "PD_RESET",                         # 1: guc anlasmasi entegresini sifirla
      "PA6": "ALERT_N"}                          # acik savak: giris kartina uyari (batarya dusuk, kapanma basliyor)
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, besleme="harici")

# --- Güç: USB-C, güç anlaşması, şarj, batarya, düğme, 3,3 V ve 5 V ------------------
gc = Sema(k.P, "Pilot Pro - USB-C guc anlasmasi, batarya sarji ve guc yolu, 3,3 V, 5 V", kagit="A1", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gc, "guc.kicad_sch", 101.6, 50.8)
gc.metin("USB TYPE-C ve GUC ANLASMASI (STUSB4500, ureticinin ornek devresi): kaynakla 20 V'a kadar anlasir, sonra P kanal cift anahtari acar.", 30, 28)
gc.metin("CC1DB/CC2DB CC uclarina bagli: batarya bitikken de kaynak 5 V verir ve sarj baslar. Istenen gerilim/akim entegrenin kalici", 30, 34)
gc.metin("bellegine uretimde I2C'den yazilir (hedef 20 V 3 A). VCHG: anahtardan sonraki sarj girisi (5-20 V).", 30, 40)
g = Izgara(50, 85, sutun=14)
k.parca(gc, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C (sarj + servis)", {"VBUS": "USBC_VBUS", "GND": "GND", "SHIELD": "GND", "CC1": "USBC_CC1", "CC2": "USBC_CC2",
        "D+": "USBC_DP", "D-": "USBC_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
k.koy(gc, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "USBC_DP", "6": "USBC_DP", "3": "USBC_DM", "4": "USBC_DM", "5": "+5V", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
k.olcum_noktasi(gc, g, "USBC_DP"); k.olcum_noktasi(gc, g, "USBC_DM")
for ag in ("USBC_VBUS", "USBC_CC1", "USBC_CC2"):
    k.iki(gc, g, *TVS25, ag, "GND", TVS25_FP)
k.C(gc, g, "4u7 50V", "USBC_VBUS", fp=C1206)
k.R(gc, g, "470R", "USBC_VBUS", "PD_VSF"); k.iki(gc, g, "Device:D_Schottky", "D", "BAT54J", "PD_VSF", "USBC_VBUS", "Diode_SMD:D_SOD-323")
k.C(gc, g, "1u 50V", "PD_VSF", fp=C0603); k.R(gc, g, "1k", "PD_VSF", "PD_VS")
g = Izgara(50, 150, sutun=14)
k.parca(gc, g, "Interface_USB:STUSB4500QTR", "U", "STUSB4500QTR", {
    "CC1": "USBC_CC1", "CC1DB": "USBC_CC1", "CC2": "USBC_CC2", "CC2DB": "USBC_CC2", "RESET": "PD_RESET", "SCL": "PWR_SCL", "SDA": "PWR_SDA",
    "DISCH": "PD_DISCH", "GND": "GND", "ADDR0": "PD_ADDR0", "ADDR1": "PD_ADDR1", "VBUS_EN_SNK": "PD_EN_SNK", "VBUS_VS_DISCH": "PD_VS",
    "ALERT": "PD_ALERT_N", "VREG_1V2": "PD_1V2", "VREG_2V7": "PD_2V7", "VSYS": "+3V3", "VDD": "PD_MID"},
    "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm", bosluk=3, dx=26)
k.C(gc, g, "1u 50V", "PD_MID", fp=C0603); k.C(gc, g, "1u", "PD_1V2"); k.C(gc, g, "1u", "PD_2V7"); k.C(gc, g, "100n", "+3V3")
k.R(gc, g, "100k", "PD_RESET", "GND"); k.R(gc, g, "100k", "PD_ADDR0", "GND"); k.R(gc, g, "100k", "PD_ADDR1", "GND")
k.R(gc, g, "10k", "+3V3", "PD_ALERT_N"); k.R(gc, g, "1k", "VCHG", "PD_DISCH")
k.bayrak(gc, g, "PD_MID")
g = Izgara(50, 200, sutun=14)
x, y = g.yer()
k.koy(gc, "Transistor_FET:SUD50P04-08", "Q", "SUD50P04-08", x, y, {"D": "USBC_VBUS", "S": "PD_MID", "G": "PD_GATE"}, "Package_TO_SOT_SMD:TO-252-2")
x, y = g.yer()
k.koy(gc, "Transistor_FET:SUD50P04-08", "Q", "SUD50P04-08", x, y, {"S": "PD_MID", "D": "VCHG", "G": "PD_GATE"}, "Package_TO_SOT_SMD:TO-252-2")
k.R(gc, g, "100k", "PD_GATE", "PD_MID"); k.R(gc, g, "22k", "PD_GATE", "PD_EN_SNK")
k.R(gc, g, "100R", "PD_GATE", "PD_SLEW"); k.C(gc, g, "100n 50V", "PD_SLEW", "VCHG", fp=C0603)
k.iki(gc, g, *TVS25, "VCHG", "GND", TVS25_FP)
k.bayrak(gc, g, "VCHG"); k.olcum_noktasi(gc, g, "VCHG")

gc.metin("SARJ ve GUC YOLU (BQ25798, alcaltan-yukselten, 750 kHz, 2,2 uH): 5-20 V giristen 4 hucreli bataryayi sarj eder ve sistemi besler.", 30, 232)
gc.metin("PROG 27k = 4 hucre, 750 kHz. Sistem (+VSYS) girisle bataryadan hangisi varsa ondan beslenir; ikisi birlikteyken batarya destekler.", 30, 238)
gc.metin("Batarya anahtari (SDRV): 'nakliye kipi'nde bataryayi tumuyle ayirir = KAPALI. Dugme (QON) ya da USB takilmasi yeniden acar.", 30, 244)
gc.metin("Sicaklik bolucusu 5k23 / 30k1 (103AT sinifi 10 k NTC). Giris akimi siniri yazilimla ayarlanir (ILIM_HIZ = REGN: donanim siniri en yuksekte).", 30, 250)
g = Izgara(50, 305, sutun=14)
k.parca(gc, g, "Battery_Management:BQ25798", "U", "BQ25798RQMR", {
    "VBUS": "VCHG", "VAC1": "VCHG", "VAC2": "VCHG", "ACDRV1": "GND", "ACDRV2": "GND", "PMID": "CHG_PMID", "SW1": "CHG_SW1", "SW2": "CHG_SW2",
    "BTST1": "CHG_BTST1", "BTST2": "CHG_BTST2", "REGN": "CHG_REGN", "SYS": "+VSYS", "BAT": "CHG_BAT", "BATP": "CHG_BATP", "SDRV": "CHG_SDRV", "GND": "GND",
    "~{QON}": "CHG_QON", "~{CE}": "GND", "SCL": "PWR_SCL", "SDA": "PWR_SDA", "~{INT}": "CHG_INT_N", "STAT": "CHG_STAT", "TS": "CHG_TS",
    "ILIM_HIZ": "CHG_REGN", "PROG": "CHG_PROG"}, "Package_DFN_QFN:Texas_RQM0029A_VQFN-29_4x4mm_P0.4mm", bosluk=3, dx=24)
k.iki(gc, g, "Device:L", "L", "2u2 XAL7030-222 (Isat 10 A)", "CHG_SW1", "CHG_SW2", "Inductor_SMD:L_Coilcraft_XAL7030-222")
k.C(gc, g, "47n 25V", "CHG_BTST1", "CHG_SW1"); k.C(gc, g, "47n 25V", "CHG_BTST2", "CHG_SW2"); k.C(gc, g, "4u7 10V", "CHG_REGN", fp=C0603)
k.R(gc, g, "27k 1%", "CHG_PROG", "GND"); k.R(gc, g, "100R", "+BATT", "CHG_BATP")
k.R(gc, g, "5k23 1%", "CHG_REGN", "CHG_TS"); k.R(gc, g, "30k1 1%", "CHG_TS", "GND"); k.R(gc, g, "0R", "BAT_T", "CHG_TS"); k.R(gc, g, "10k", "CHG_TS", "GND", dnp=True)
g = Izgara(140, 333, sutun=12)
for ag, n in (("VCHG", 2), ("CHG_PMID", 3), ("+VSYS", 5), ("CHG_BAT", 2)):
    for _ in range(n):
        k.C(gc, g, "10u 35V", ag, fp=C1206)
g.satir()
for ag in ("VCHG", "CHG_PMID", "+VSYS"):
    k.C(gc, g, "100n 50V", ag, fp=C0603)
k.R(gc, g, "4k7", "+3V3", "PWR_SCL"); k.R(gc, g, "4k7", "+3V3", "PWR_SDA"); k.R(gc, g, "10k", "+3V3", "CHG_INT_N")
k.iki(gc, g, "Device:LED", "D", "LED turuncu (sarj)", "CHG_STAT", "CHG_LED_A", "LED_SMD:LED_0603_1608Metric"); k.R(gc, g, "1k5", "+3V3", "CHG_LED_A")
k.olcum_noktasi(gc, g, "+VSYS"); k.olcum_noktasi(gc, g, "CHG_REGN")

gc.metin("BATARYA (4 hucreli akilli Li-ion paket, kendi koruma ve olcer devresiyle; 5 kontak: +, SCL, SDA, sicaklik, -). Paketin olceri guc", 430, 215)
gc.metin("islemcisinin I2C hattindadir. Batarya anahtari N kanal MOSFET: akaci bataryada, kaynagi sarj entegresinde (kapaliyken sisteme akim gecmez).", 430, 221)
g = Izgara(450, 285, sutun=12)
k.parca(gc, g, "Connector_Generic:Conn_01x05", "J", "Batarya (4S akilli paket)", {"Pin_1": "+BATT", "Pin_2": "BAT_SCL", "Pin_3": "BAT_SDA", "Pin_4": "BAT_T", "Pin_5": "GND"},
        "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical", dx=8)
x, y = g.yer()
k.koy(gc, "Device:Q_NMOS", "Q", "BSC014N04LS", x, y, {"D": "+BATT", "G": "CHG_SDRV", "S": "CHG_BAT"}, "Package_TO_SOT_SMD:TDSON-8-1")
k.R(gc, g, "100R", "BAT_SCL", "PWR_SCL"); k.R(gc, g, "100R", "BAT_SDA", "PWR_SDA")
k.C(gc, g, "10u 35V", "+BATT", fp=C1206); k.iki(gc, g, "Device:D_TVS", "D", "SMBJ18A", "+BATT", "GND", "Diode_SMD:D_SMB")
k.olcum_noktasi(gc, g, "+BATT")

gc.metin("GUC DUGMESI: sarj entegresinin QON ucuna baglidir (ic yukari cekme). Kapaliyken basinca batarya anahtari acilir ve kart calisir;", 430, 340)
gc.metin("uzun basinca (yaklasik 10 s) entegre sistemi sifirlar (donanim sifirlamasi, yazilimdan bagimsiz). Cift diyot dugmeyi iki islemciye", 430, 346)
gc.metin("ayri ayri duyurur; islemciler gerilimsizken QON'u etkilemez. KAPATMA: guc islemcisi sarj entegresine 'nakliye kipi' komutu verir.", 430, 352)
g = Izgara(450, 395, sutun=12)
k.parca(gc, g, "Connector_Generic_MountingPin:Conn_01x02_MountingPin", "J", "Guc dugmesi", {"Pin_1": "CHG_QON", "Pin_2": "GND", "MountPin": "GND"},
        "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal", dx=8)
x, y = g.yer()
k.koy(gc, "Diode:BAT54C", "D", "BAT54C", x, y, {"1": "PWR_BTN_N", "2": "PWR_BTN_M", "3": "CHG_QON"}, SOT23)
k.C(gc, g, "100n", "CHG_QON"); k.R(gc, g, "100k", "+3V3", "PWR_BTN_M")

gc.metin("3,3 V ve 5 V (AP63203 / AP63205, +VSYS'ten, 2 A): batarya bagliyken (nakliye kipi disinda) surekli aciktir. 3,3 V: guc islemcisi,", 430, 440)
gc.metin("giris karti, sayisal devreler. 5 V: CAN alici-vericileri, sesli uyarici, 2. adimdaki USB portlari. Dugum ve Radio kartindaki devrelerin aynisi.", 430, 446)
g = Izgara(450, 490, sutun=12)
for ad, parca, ag, bobin in (("3V3", "AP63203", "+3V3", "3u3 XAL4020-332"), ("5V", "AP63205", "+5V", "4u7 XAL4020-472")):
    k.parca(gc, g, "Regulator_Switching:%sWU" % parca, "U", parca + "QWU", {"IN": "+VSYS", "EN": "EN_" + ad, "GND": "GND", "SW": "SW_" + ad, "BST": "BST_" + ad, "FB": ag}, TSOT6)
    k.R(gc, g, "100k", "+VSYS", "EN_" + ad); k.C(gc, g, "10u 50V", "+VSYS", fp=C1206); k.C(gc, g, "100n", "BST_" + ad, "SW_" + ad)
    k.iki(gc, g, "Device:L", "L", bobin, "SW_" + ad, ag, XAL)
    k.C(gc, g, "22u 16V", ag, fp=C1206); k.C(gc, g, "22u 16V", ag, fp=C1206); k.bayrak(gc, g, ag); k.olcum_noktasi(gc, g, ag)
    g.satir()
gc.yaz(os.path.join(BURASI, "guc.kicad_sch"))

# --- Kumanda radyosu ve giriş kartı bağlantısı ---------------------------------------
rd = Sema(k.P, "Pilot Pro - kumanda radyosu, radyo beslemesi, giris karti baglantisi, sesli uyarici", kagit="A2", tarih=k.T, ust=kok, ad="Radyo", genel_etiket=True)
kok.alt_sayfa(rd, "radyo.kicad_sch", 177.8, 50.8)
rd.metin("KUMANDA RADYO MODULU (RFD900ux-SMT; 868 MHz icin RFD868ux-SMT). Baglanti RX kartindakinin ve Pilot 12'dekinin aynisi:", 30, 28)
rd.metin("radyoyu giris kartindaki kumanda islemcisi dogrudan surer (yassi kablo). Jetson ve guc islemcisi kumanda yolunun disindadir.", 30, 34)
k.koy(rd, "operfly:RFD900ux-SMT", "U", "RFD900ux-SMT (secenek: RFD868ux-SMT)", 100, 90, {
    "+5V": "+5V3_RADIO", "GND": "GND", "RX": "RADIO_RX_M", "TX": "RADIO_TXD", "RTS": "RADIO_RTS", "CTS": "RADIO_CTS_M",
    "SWO": "RADIO_SWO", "ANT1": "RADIO_ANT1", "ANT2": "RADIO_ANT2", "+3V3_OUT": "RADIO_3V3"}, "operfly_ayak:RFDesign_RFD900ux-SMT")
g = Izgara(50, 155, sutun=9)
for a, b in (("RADIO_RXD", "RADIO_RX_M"), ("RADIO_CTS", "RADIO_CTS_M"), ("RADIO_BOOT_N", "RADIO_SWO")):
    k.R(rd, g, "470R", a, b)
k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206); k.C(rd, g, "100n", "+5V3_RADIO"); k.C(rd, g, "100p", "+5V3_RADIO")
for ag in ("RADIO_SWO", "RADIO_3V3", "RADIO_TXD"):
    k.olcum_noktasi(rd, g, ag)
g.satir()
for i in (1, 2):
    x, y = g.yer(); g.yer()
    k.koy(rd, "Connector:Conn_Coaxial", "J", "ANT %d (SMA)" % i, x + 5, y, {"In": "RADIO_ANT%d" % i, "Ext": "GND"}, "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount")

rd.metin("RADYO BESLEMESI (AP63201, +VSYS -> 5,3 V, 2 A, sabit frekansli): RX kartindaki devrenin aynisi. Cikis = 0,8 V x (1 + 169k / 30k1) = 5,29 V.", 270, 28)
rd.metin("Besleme sifirlamada ACIKTIR; kumanda islemcisi RADIO_OFF = 1 ile keser.", 270, 34)
g = Izgara(290, 80, sutun=9)
k.parca(rd, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+VSYS", "EN": "RADIO_EN", "GND": "GND", "SW": "SW_RADIO", "BST": "BST_RADIO", "FB": "FB_RADIO"}, TSOT6)
k.R(rd, g, "100k", "+VSYS", "RADIO_EN"); k.C(rd, g, "10u 50V", "+VSYS", fp=C1206); k.C(rd, g, "100n", "BST_RADIO", "SW_RADIO")
k.iki(rd, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_RADIO", "+5V3_RADIO", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206); k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206)
g.satir()
k.R(rd, g, "169k 1%", "+5V3_RADIO", "FB_RADIO"); k.R(rd, g, "30k1 1%", "FB_RADIO", "GND"); k.C(rd, g, "100p", "+5V3_RADIO", "FB_RADIO")
k.bayrak(rd, g, "+5V3_RADIO")
x, y = g.yer()
k.koy(rd, N7002[0], N7002[1], N7002[2], x, y, {"D": "RADIO_EN", "S": "GND", "G": "RADIO_OFF"}, SOT23)
k.R(rd, g, "100k", "RADIO_OFF", "GND")

rd.metin("GIRIS KARTI BAGLANTISI (20 kontakli yassi kablo): uc sirasi 13_DOKUMANTASYON/KUMANDA_ARAYUZU.md ile birebir. Pilot Pro'da farklar:", 270, 150)
rd.metin("I2C guc islemcisine gider (iki islemci arasi baglanti), PWR_HOLD kullanilmaz (gucu guc islemcisi tutar), USB 2. adimda Jetson'a baglanir.", 270, 156)
ANA = ["GND", "+3V3", "+3V3", "GND", "RADIO_RXD", "RADIO_TXD", "RADIO_CTS", "RADIO_RTS", "RADIO_OFF", "RADIO_BOOT_N",
       "GND", "KUM_USB_DM", "KUM_USB_DP", "GND", "I2C_SCL", "I2C_SDA", "ALERT_N", "PWR_BTN_N", None, "BUZZER"]
ag = {"Pin_%d" % (i + 1): a for i, a in enumerate(ANA) if a}
ag["MountPin"] = "GND"
k.koy(rd, "Connector_Generic_MountingPin:Conn_01x20_MountingPin", "J", "Giris karti (FFC 20)", 300, 225, ag,
      "Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
g = Izgara(350, 200, sutun=8)
x, y = g.yer(); g.yer()
k.koy(rd, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "KUM_USB_DP", "6": "KUM_USB_DP", "3": "KUM_USB_DM", "4": "KUM_USB_DM", "5": "+5V", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
k.olcum_noktasi(rd, g, "KUM_USB_DP"); k.olcum_noktasi(rd, g, "KUM_USB_DM")
g.satir()
x, y = g.yer(); g.yer()
k.koy(rd, "Device:Buzzer", "BZ", "PKLCS1212E4001", x + 5, y, {"+": "+5V", "-": "BUZZER_K"}, "Buzzer_Beeper:Buzzer_Murata_PKLCS1212E")
k.R(rd, g, "1k", "+5V", "BUZZER_K")
x, y = g.yer()
k.koy(rd, N7002[0], N7002[1], N7002[2], x, y, {"D": "BUZZER_K", "S": "GND", "G": "BUZZER"}, SOT23)
k.R(rd, g, "100k", "BUZZER", "GND")
rd.yaz(os.path.join(BURASI, "radyo.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_pilotpro.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gc, rd], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_pilotpro (kok + 3 sayfa)")
