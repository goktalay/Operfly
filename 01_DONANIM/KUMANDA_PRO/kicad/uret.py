"""Operfly Pilot Pro ana kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_PRO operfly_pilotpro`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
1. ADIM: güç işlemcisi (düğüm devresi), USB Type-C güç anlaşması, 4 hücreli batarya şarjı ve güç yolu, 3,3 V ve 5 V,
güç düğmesi, kumanda radyosu ve giriş kartı bağlantısı. Bu kadarıyla kart kumanda olarak çalışır.
2. ADIM, ilk bölüm: Jetson çekirdeği ve beslemesi, NVMe, USB göbeği, omurga Ethernet'i, fan (Vision kartındaki devreler).
3. ADIM: geniş bant radyo (Radio kartındaki devre) ve ikinci Ethernet portu (Vision'daki I210 devresi).
4. ADIM: ekran arayüzü: HDMI görüntü çıkışı, 12 V panel beslemesi, parlaklık (panelden bağımsız; README'de).

Devre değerleri üretici belgelerindendir: BQ25798 (SLUSDV2C: uç açıklamaları, Tablo 7-1, bölüm 7.3.9.5, 7.3.12, 8.2),
STUSB4500 (DS12499 Rev 3, Şekil 10 "Typical schematic with MCU"), AP6320x (düğüm ve RX kartındaki devreler),
RFD900ux (V1.3; RX kartındaki bağlantı), Jetson Orin NX (uç tablosu `jetson_uclari.py`; devreler Vision kartından),
TPS26630 (Vision kartındaki sigorta), TPS54560B (SLVSF00; Cell ve Power kartındaki devre), USB2514B (PC adaptöründeki devre),
HDMI (Jetson Orin NX/Nano tasarım kılavuzu DG-10931 bölüm 9; açık kaynaklı bir taşıyıcı kartın üretilmiş HDMI devresi).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, XAL, Izgara, Kart  # noqa: E402
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
kok.metin("Sematik betikle uretilir: 01_DONANIM/KUMANDA_PRO/kicad/uret.py. Ekran arayuzu panelden bagimsizdir (HDMI + 12 V + USB dokunmatik + PWM).", 25.4, 33.02, 1.6)

EK = {"PB10": "PWR_SCL", "PB11": "PWR_SDA",      # I2C2: sarj entegresi, guc anlasmasi entegresi, bataryanin kendi olceri
      "PB3": "I2C_SCL", "PB4": "I2C_SDA",        # I2C3 (kole): giris kartindaki kumanda islemcisiyle dogrudan baglanti
      "PA0": "CHG_INT_N", "PA1": "PD_ALERT_N",   # kesme girisleri
      "PA4": "PWR_BTN_M",                        # guc dugmesi (0 = basili)
      "PA5": "PD_RESET",                         # 1: guc anlasmasi entegresini sifirla
      "PA6": "ALERT_N",                          # acik savak: giris kartina uyari (batarya dusuk, kapanma basliyor)
      "PA2": "JET_IMON",                         # ADC1_IN2: Jetson akimi (4 A -> 3,0 V)
      "PA3": "JET_VIN_EN",                       # 1: Jetson'a besleme ver (sifirlamada kapali)
      "PA7": "JET_POWER_EN",                     # 1: modul acilir
      "PA8": "JET_SHDN_REQ_N",                   # 0: modul kapanmak istiyor -> POWER_EN indirilir
      "PB0": "JET_RESET", "PB1": "JET_RECOVERY", # 1: SYS_RESET* / FORCE_RECOVERY* dusuge cekilir
      "PC7": "JET_MODULE_ID",                    # 1: 5-20 V destekli modul; 0: yalniz 5 V'luk eski modul -> besleme VERILMEZ
      "PD2": "JET_RUN",                          # 1: tasiyici 3,3 V'u acik (modul SYS_RESET*'i birakti)
      "PD3": "PWR_FLT_N",                        # 0: Jetson sigortasi hata verdi
      "PB6": "MCU_TX", "PB7": "MCU_RX",          # USART1: Jetson UART1 (seviye ceviriciden)
      "PC6": "FAN_TACH",                         # TIM3_CH1: fan devir darbesi
      "PA9/PA11": "PWR_USB_DM", "PA10/PA12": "PWR_USB_DP"}   # USB: gobegin 2. portu (PA11 = D-, PA12 = D+)
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, besleme="harici", ethernet=True)
C1210 = "Capacitor_SMD:C_1210_3225Metric"
TANTAL = "Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D"

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
rd.metin("I2C guc islemcisine gider (iki islemci arasi baglanti), PWR_HOLD kullanilmaz (gucu guc islemcisi tutar), USB gobegin 1. portuna gider.", 270, 156)
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
g.satir()
x, y = g.yer(); g.yer()
k.koy(rd, "Device:Buzzer", "BZ", "PKLCS1212E4001", x + 5, y, {"+": "+5V", "-": "BUZZER_K"}, "Buzzer_Beeper:Buzzer_Murata_PKLCS1212E")
k.R(rd, g, "1k", "+5V", "BUZZER_K")
x, y = g.yer()
k.koy(rd, N7002[0], N7002[1], N7002[2], x, y, {"D": "BUZZER_K", "S": "GND", "G": "BUZZER"}, SOT23)
k.R(rd, g, "100k", "BUZZER", "GND")
rd.yaz(os.path.join(BURASI, "radyo.kicad_sch"))

# --- Jetson: besleme, soket, denetim ---------------------------------------------------
jt = Sema(k.P, "Pilot Pro - Jetson Orin NX soketi, beslemesi ve denetim devreleri", kagit="A1", tarih=k.T, ust=kok, ad="Jetson", genel_etiket=True)
kok.alt_sayfa(jt, "jetson.kicad_sch", 254.0, 50.8)
jt.birim_araligi = 200
jt.metin("JETSON SOKETI (260 uclu SO-DIMM). Birimler: guc ve denetim | PCIe, Ethernet, USB | dusuk hizli giris-cikislar | goruntu uclari (HDMI, Ekran sayfasi).", 30, 25)
jt.metin("Uc tablosu uretici veri sayfasindan (10_ORTAK_ARACLAR/kicad/jetson_uclari.py). Devreler Vision kartindakilerin aynisidir; PCIE1 ikinci Ethernet portuna gider, PCIE2 bostur.", 30, 31)
J = {"VDD_IN": "+VJET", "GND": "GND", "POWER_EN": "JET_POWER_EN_R", "SYS_RESET*": "JET_SYS_RESET_N", "SHUTDOWN_REQ*": "JET_SHDN_REQ_HV",
     "FORCE_RECOVERY*": "JET_FRC_N", "MODULE_ID": "JET_MODULE_ID", "MOD_SLEEP*": "JET_MOD_SLEEP_N", "SLEEP/WAKE*": "JET_SLEEP_WAKE_N",
     "PCIE0_CLK_P": "M2_CLK_P", "PCIE0_CLK_N": "M2_CLK_N", "PCIE0_RST*": "M2_RST_N", "PCIE0_CLKREQ*": "M2_CLKREQ_N", "PCIE_WAKE*": "PCIE_WAKE_N",
     "USB0_D_P": "USBC_DP", "USB0_D_N": "USBC_DM", "GPIO00": "USB0_VBUS_DET_N", "USB1_D_P": "HUB_UP_DP", "USB1_D_N": "HUB_UP_DM",
     "UART1_TXD": "JET_UART_TX_1V8", "UART1_RXD": "JET_UART_RX_1V8", "UART2_TXD": "JET_DBG_TX", "UART2_RXD": "JET_DBG_RX", "GPIO14": "JET_FAN_PWM_1V8", "GPIO13": "JET_BL_PWM_1V8",
     "DP1_TXD0_P": "HDMI_D2_J_P", "DP1_TXD0_N": "HDMI_D2_J_N", "DP1_TXD1_P": "HDMI_D1_J_P", "DP1_TXD1_N": "HDMI_D1_J_N",
     "DP1_TXD2_P": "HDMI_D0_J_P", "DP1_TXD2_N": "HDMI_D0_J_N", "DP1_TXD3_P": "HDMI_CK_J_P", "DP1_TXD3_N": "HDMI_CK_J_N",
     "DP1_AUX_P": "HDMI_SCL_3V3", "DP1_AUX_N": "HDMI_SDA_3V3", "DP1_HPD": "HDMI_HPD_N_1V8"}   # HDMI kipi (Ekran sayfasi)
for l in range(4):
    for s_ in "PN":
        J["PCIE0_RX%d_%s" % (l, s_)] = "M2_PER%d_%s" % (l, s_)
        J["PCIE0_TX%d_%s" % (l, s_)] = "J_PCIE0_TX%d_%s" % (l, s_)
        J["GBE_MDI%d_%s" % (l, s_)] = "JGBE_MDI%d_%s" % (l, s_)
J.update({"PCIE1_RX0_P": "E1_PET_C_P", "PCIE1_RX0_N": "E1_PET_C_N", "PCIE1_TX0_P": "J_PCIE1_TX_P", "PCIE1_TX0_N": "J_PCIE1_TX_N",
          "PCIE1_CLK_P": "E1_CLK_P", "PCIE1_CLK_N": "E1_CLK_N", "PCIE1_RST*": "E1_RST_N", "PCIE1_CLKREQ*": "E1_CLKREQ_N"})   # ikinci Ethernet portu
k.koy(jt, "operfly:Jetson_Orin_NX", "J", "Jetson Orin NX", 110, 150, J, "Connector_PCBEdge:SODIMM-260_DDR4_H4.0-5.2_OrientationStd_Socket")

jt.metin("DENETIM (Vision ile ayni): POWER_EN guc islemcisinden (1k seri). SHUTDOWN_REQ* modulde besleme gerilimine cekilidir -> 100k/22k ile islemciye.", 30, 290)
jt.metin("SYS_RESET* ve FORCE_RECOVERY* 1,8 V hatlardir: islemci yalnizca transistorle DUSUGE ceker. MODULE_ID: Orin'de bosta (100k ile 3,3 V = 1).", 30, 296)
g = Izgara(50, 335, sutun=14)
k.R(jt, g, "1k", "JET_POWER_EN", "JET_POWER_EN_R"); k.R(jt, g, "100k", "JET_POWER_EN", "GND")
k.R(jt, g, "100k 1%", "JET_SHDN_REQ_HV", "JET_SHDN_REQ_N"); k.R(jt, g, "22k 1%", "JET_SHDN_REQ_N", "GND"); k.C(jt, g, "1n", "JET_SHDN_REQ_N")
k.R(jt, g, "100k", "+3V3", "JET_MODULE_ID")
for ag, kapi in (("JET_SYS_RESET_N", "JET_RESET"), ("JET_FRC_N", "JET_RECOVERY")):
    x, y = g.yer()
    k.koy(jt, N7002[0], N7002[1], N7002[2], x, y, {"D": ag, "S": "GND", "G": kapi}, SOT23)
    k.R(jt, g, "100k", kapi, "GND")
for ag in ("JET_SYS_RESET_N", "JET_FRC_N", "JET_MOD_SLEEP_N", "JET_SLEEP_WAKE_N", "JET_DBG_TX", "JET_DBG_RX"):
    k.olcum_noktasi(jt, g, ag)
g.satir()
for l in range(4):
    for s_ in "PN":
        k.C(jt, g, "220n", "J_PCIE0_TX%d_%s" % (l, s_), "M2_PET%d_%s" % (l, s_))
k.R(jt, g, "100k", "USBC_VBUS", "USB_VBUS_G"); k.R(jt, g, "100k", "USB_VBUS_G", "GND")
x, y = g.yer()
k.koy(jt, N7002[0], N7002[1], N7002[2], x, y, {"D": "USB0_VBUS_DET_N", "S": "GND", "G": "USB_VBUS_G"}, SOT23)

jt.metin("JETSON BESLEMESI (TPS26630, akim siniri 18 / 4k53 = 4 A): modul 5-20 V kabul eder, batarya gerilimi (+VSYS, 12-17 V) dogrudan verilir.", 420, 290)
jt.metin("Sigorta 10,4 V altinda ve 18,4 V ustunde keser. Guc islemcisi once MODULE_ID'yi okur, sonra JET_VIN_EN verir. IMON 27k (4 A -> 3,0 V).", 420, 296)
k.koy(jt, "Power_Management:TPS26630RGE", "U", "TPS26630RGER", 470, 345, {
    "IN": "+VSYS", "IN_SYS": "+VSYS", "UVLO": "JET_UVLO", "OVP": "JET_OVP", "GND": "GND", "MODE": "GND", "dVdT": "JET_DVDT", "ILIM": "JET_ILIM",
    "~{SHDN}": "JET_VIN_EN", "IMON": "JET_IMON", "~{FLT}": "PWR_FLT_N", "PGTH": "JET_PGTH", "OUT": "+VJET"},
    "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias")
g = Izgara(530, 335, sutun=12)
k.C(jt, g, "100n 50V", "+VSYS", fp=C0603); k.C(jt, g, "1u 25V", "+VJET", fp=C0603)
k.R(jt, g, "4k53 1%", "JET_ILIM", "GND"); k.C(jt, g, "47n", "JET_DVDT"); k.R(jt, g, "27k 1%", "JET_IMON", "GND"); k.C(jt, g, "100n", "JET_IMON")
k.R(jt, g, "47k", "JET_VIN_EN", "GND"); k.R(jt, g, "100k 1%", "+VJET", "JET_PGTH"); k.R(jt, g, "13k7 1%", "JET_PGTH", "GND")
k.R(jt, g, "100k 1%", "+VSYS", "JET_UVLO"); k.R(jt, g, "13k 1%", "JET_UVLO", "GND")
g.satir()
k.R(jt, g, "100k 1%", "+VSYS", "JET_OVP"); k.R(jt, g, "6k98 1%", "JET_OVP", "GND"); k.R(jt, g, "10k", "+3V3", "PWR_FLT_N")
k.C(jt, g, "100u 25V", "+VJET", fp=TANTAL); k.C(jt, g, "100u 25V", "+VJET", fp=TANTAL); k.olcum_noktasi(jt, g, "+VJET")

jt.metin("TASIYICI 3,3 V'u (TPS54560B, +VSYS'ten, 5 A): NVMe, 1,8 V regulatoru ve ileride ikinci Ethernet denetleyicisi icin. Modul SYS_RESET*'i", 420, 410)
jt.metin("biraktiginda acilir; ondan once kart Jetson uclarina gerilim vermez (uretici kurali). Cikis = 0,8 V x (1 + 31k6 / 10k2) = 3,28 V. JET_RUN: ray acik.", 420, 416)
g = Izgara(440, 460, sutun=16, dx=24)
k.parca(jt, g, "Regulator_Switching:TPS54560BDDA", "U", "TPS54560BDDAR", {"VIN": "+VSYS", "EN": "JET_SYS_RESET_N", "RT/CLK": "J33_RT", "FB": "J33_FB",
        "COMP": "J33_COMP", "BOOT": "J33_BOOT", "SW": "J33_SW", "GND": "GND"}, "Package_SO:Texas_R-PDSO-G8_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias", bosluk=2, dx=22)
k.C(jt, g, "10u 50V", "+VSYS", fp=C1206); k.C(jt, g, "10u 50V", "+VSYS", fp=C1206); k.C(jt, g, "100n 50V", "+VSYS", fp=C0603)
k.R(jt, g, "243k 1%", "J33_RT", "GND"); k.R(jt, g, "13k", "J33_COMP", "J33_COMP_RC"); k.C(jt, g, "4n7", "J33_COMP_RC"); k.C(jt, g, "47p", "J33_COMP")
k.C(jt, g, "100n 25V", "J33_BOOT", "J33_SW", fp=C0603)
k.iki(jt, g, "Device:D_Schottky", "D", "PDS760 (60 V, 7 A)", "J33_SW", "GND", "Diode_SMD:D_PowerDI-5")
k.iki(jt, g, "Device:L", "L", "10u XAL7070-103", "J33_SW", "+3V3_JET", "Inductor_SMD:L_Coilcraft_XAL7070-XXX")
g.satir()
for _ in range(3):
    k.C(jt, g, "47u 16V", "+3V3_JET", fp=C1210)
k.R(jt, g, "31k6 1%", "+3V3_JET", "J33_FB"); k.R(jt, g, "10k2 1%", "J33_FB", "GND")
k.R(jt, g, "10k", "+3V3_JET", "JET_RUN"); k.R(jt, g, "100k", "JET_RUN", "GND")
k.bayrak(jt, g, "+3V3_JET"); k.olcum_noktasi(jt, g, "+3V3_JET")
k.parca(jt, g, "Regulator_Linear:LP5907MFX-1.8", "U", "LP5907MFX-1.8", {"IN": "+3V3_JET", "EN": "+3V3_JET", "GND": "GND", "OUT": "+1V8_JET"}, "Package_TO_SOT_SMD:SOT-23-5", bosluk=1, dx=14)
k.C(jt, g, "1u", "+3V3_JET"); k.C(jt, g, "1u", "+1V8_JET"); k.olcum_noktasi(jt, g, "+1V8_JET")
jt.yaz(os.path.join(BURASI, "jetson.kicad_sch"))

# --- Çevre: NVMe, USB göbeği, dış USB, omurga Ethernet'i, seviye çevirici, fan -------------
cv = Sema(k.P, "Pilot Pro - NVMe, USB gobegi, omurga Ethernet'i, seviye cevirici, fan", kagit="A1", tarih=k.T, ust=kok, ad="Cevre", genel_etiket=True)
kok.alt_sayfa(cv, "cevre.kicad_sch", 330.2, 50.8)
cv.metin("M.2 NVMe (Key M, PCIE0, dort serit; Vision ile ayni): soketin PER uclari Jetson'in alicilarina dogrudan, PET uclari vericilerine 220 nF ile.", 30, 28)
M = {"3.3V": "+3V3_JET", "GND": "GND", "~{PERST}": "M2_RST_N", "~{CLKREQ}": "M2_CLKREQ_N", "~{PEWAKE}": "PCIE_WAKE_N", "REFCLKp": "M2_CLK_P", "REFCLKn": "M2_CLK_N",
     "DEVSLP": "M2_DEVSLP", "PERp0/SATA-B-": "M2_PER0_P", "PERn0/SATA-B+": "M2_PER0_N", "PETp0/SATA-A+": "M2_PET0_P", "PETn0/SATA-A-": "M2_PET0_N"}
for l in (1, 2, 3):
    M.update({"PERp%d" % l: "M2_PER%d_P" % l, "PERn%d" % l: "M2_PER%d_N" % l, "PETp%d" % l: "M2_PET%d_P" % l, "PETn%d" % l: "M2_PET%d_N" % l})
k.koy(cv, "Connector:Bus_M.2_Socket_M", "J", "M.2 Key M (NVMe 2242/2280)", 90, 120, M, "Connector_PCBEdge:TE_M.2_M_2x38-1MP_P0.5mm")
g = Izgara(170, 70, sutun=8)
k.R(cv, g, "10k", "M2_DEVSLP", "GND"); k.C(cv, g, "22u 10V", "+3V3_JET", fp=C1206); k.C(cv, g, "22u 10V", "+3V3_JET", fp=C1206)
for _ in range(3):
    k.C(cv, g, "100n", "+3V3_JET")

cv.metin("USB GOBEGI (USB2514B, 24 MHz; PC adaptorundeki devre): Jetson USB1'den dort port. 1: kumanda islemcisi (giris karti), 2: guc islemcisi,", 380, 28)
cv.metin("3: dokunmatik ekran konnektoru, 4: dis USB-A (0,5 A sinirli). Gobek surekli beslenir ama Jetson'in 3,3 V'u yokken sifirlamada tutulur.", 380, 34)
k.koy(cv, "Interface_USB:USB2514B_Bi", "U", "USB2514Bi-AEZG", 470, 120, {
    "USBDP_UP": "HUB_UP_DP", "USBDM_UP": "HUB_UP_DM", "USBDP_DN1/PRT_DIS_P1": "KUM_USB_DP", "USBDM_DN1/PRT_DIS_M1": "KUM_USB_DM",
    "USBDP_DN2/PRT_DIS_P2": "PWR_USB_DP", "USBDM_DN2/PRT_DIS_M2": "PWR_USB_DM", "USBDP_DN3/PRT_DIS_P3": "TCH_USB_DP", "USBDM_DN3/PRT_DIS_M3": "TCH_USB_DM",
    "USBDP_DN4/PRT_DIS_P4": "EXT_USB_DP", "USBDM_DN4/PRT_DIS_M4": "EXT_USB_DM",
    "VDD33": "+3V3", "VDDA33": "+3V3", "VSS": "GND", "TEST": "GND", "RESET_N": "HUB_RESET_N", "VBUS_DET": "HUB_VBUS_DET",
    "CRFILT": "HUB_CRFILT", "PLLFILT": "HUB_PLLFILT", "RBIAS": "HUB_RBIAS", "XTALIN/CLKIN": "HUB_XI", "XTALOUT": "HUB_XO",
    "HS_IND/CFG_SEL1": "HUB_CFG1", "SCL/SMBCLK/CFG_SEL0": "HUB_CFG0", "SDA/SMBDATA/NON_REM1": "HUB_NR1", "SUSP_IND/LOCAL_PWR/NON_REM0": "HUB_NR0",
}, "Package_DFN_QFN:QFN-36-1EP_6x6mm_P0.5mm_EP3.7x3.7mm")
g = Izgara(390, 215, sutun=14)
k.koy(cv, "Device:Crystal_GND24", "Y", "24 MHz", *g.yer(), {"1": "HUB_XI", "3": "HUB_XO", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(cv, g, "18p", "HUB_XI"); k.C(cv, g, "18p", "HUB_XO")
k.R(cv, g, "12k 1%", "HUB_RBIAS", "GND"); k.C(cv, g, "100n", "HUB_CRFILT"); k.C(cv, g, "100n", "HUB_PLLFILT")
k.R(cv, g, "10k", "+3V3_JET", "HUB_RESET_N"); k.R(cv, g, "100k", "HUB_RESET_N", "GND"); k.R(cv, g, "1k", "+3V3_JET", "HUB_VBUS_DET")
k.R(cv, g, "100k", "HUB_CFG1", "GND"); k.R(cv, g, "100k", "HUB_CFG0", "GND"); k.R(cv, g, "100k", "+3V3", "HUB_NR1"); k.R(cv, g, "100k", "HUB_NR0", "GND")
g.satir()
for _ in range(6):
    k.C(cv, g, "100n", "+3V3")
k.C(cv, g, "4u7", "+3V3", fp=C0603)

cv.metin("DIS USB-A PORTU (TPS2051C, 0,5 A) ve DOKUNMATIK EKRAN USB'si (JST-GH 4: +5 V, D-, D+, GND). Ikisi de Jetson acikken beslenir.", 380, 290)
g = Izgara(400, 330, sutun=14)
k.parca(cv, g, "Power_Management:TPS2051CDBV", "U", "TPS2051CDBV", {"IN": "+5V", "GND": "GND", "EN": "JET_RUN", "~{FLT}": "EXT_USB_FLT_N", "OUT": "EXT_USB_5V"},
        "Package_TO_SOT_SMD:SOT-23-5", bosluk=1, dx=14)
k.C(cv, g, "1u", "+5V"); k.C(cv, g, "100u 10V", "EXT_USB_5V", fp=TANTAL); k.R(cv, g, "10k", "+3V3", "EXT_USB_FLT_N"); k.olcum_noktasi(cv, g, "EXT_USB_FLT_N")
k.parca(cv, g, "Connector:USB_A", "J", "USB-A (dis)", {"VBUS": "EXT_USB_5V", "D-": "EXT_USB_DM", "D+": "EXT_USB_DP", "GND": "GND", "Shield": "GND"},
        "Connector_USB:USB_A_Molex_67643_Horizontal", bosluk=1, dx=10)
x, y = g.yer(); g.yer()
k.koy(cv, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "EXT_USB_DP", "6": "EXT_USB_DP", "3": "EXT_USB_DM", "4": "EXT_USB_DM", "5": "EXT_USB_5V", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
g.satir()
k.parca(cv, g, "Power_Management:TPS2051CDBV", "U", "TPS2051CDBV", {"IN": "+5V", "GND": "GND", "EN": "JET_RUN", "~{FLT}": "TCH_USB_FLT_N", "OUT": "TCH_USB_5V"},
        "Package_TO_SOT_SMD:SOT-23-5", bosluk=1, dx=14)
k.C(cv, g, "1u", "+5V"); k.C(cv, g, "22u 10V", "TCH_USB_5V", fp=C1206); k.R(cv, g, "10k", "+3V3", "TCH_USB_FLT_N"); k.olcum_noktasi(cv, g, "TCH_USB_FLT_N")
k.parca(cv, g, "Connector_Generic_MountingPin:Conn_01x04_MountingPin", "J", "Dokunmatik ekran (USB)", {"Pin_1": "TCH_USB_5V", "Pin_2": "TCH_USB_DM", "Pin_3": "TCH_USB_DP",
        "Pin_4": "GND", "MountPin": "GND"}, "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
x, y = g.yer(); g.yer()
k.koy(cv, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "TCH_USB_DP", "6": "TCH_USB_DP", "3": "TCH_USB_DM", "4": "TCH_USB_DM", "5": "TCH_USB_5V", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")

cv.metin("OMURGA ETHERNET'I (Vision ile ayni): Jetson'in kendi gigabit portu trafo (TG111-MSC13LF) uzerinden omurga fisinin dort ciftine gider.", 30, 250)
cv.metin("Yer radyosu (Ground Radio), Base ve bilgisayar bu porttan baglanir. Orta uclar: Jetson tarafi 100n -> GND, kablo tarafi 75R -> 1 nF 2 kV.", 30, 256)
tr = {}
for c, i, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", range(4), ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
    tr.update({str(cp): "JGBE_MDI%d_P" % i, str(cm): "JGBE_MDI%d_N" % i, str(cc): "BB_CT_%s" % c,
               str(kp_): "ETH_%s+" % c, str(km_): "ETH_%s-" % c, str(kc_): "BB_KCT_%s" % c})
k.koy(cv, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", 80, 320, tr, "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13")
g = Izgara(150, 300, sutun=9, dx=24)
for c in "ABCD":
    k.C(cv, g, "100n", "BB_CT_%s" % c)
for c in "ABCD":
    k.R(cv, g, "75R", "BB_KCT_%s" % c, "BB_BS")
k.C(cv, g, "1n 2kV", "BB_BS", fp=C1206)

cv.metin("SEVIYE CEVIRICI (TXS0104E, 1,8 V <-> 3,3 V): Jetson UART1 <-> guc islemcisi (USART1), fan PWM (GPIO14), ekran parlakligi PWM (GPIO13). Jetson kapaliyken uclarini birakir.", 30, 400)
g = Izgara(50, 445, sutun=10)
k.parca(cv, g, "Logic_LevelTranslator:TXS0104EPW", "U", "TXS0104EPW", {"V_{CCA}": "+1V8_JET", "V_{CCB}": "+3V3", "OE": "+1V8_JET", "GND": "GND",
        "A1": "JET_UART_TX_1V8", "B1": "MCU_RX", "A2": "JET_UART_RX_1V8", "B2": "MCU_TX", "A3": "JET_BL_PWM_1V8", "B3": "BL_PWM_3V3", "A4": "JET_FAN_PWM_1V8", "B4": "FAN_PWM_3V3"},
        "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", bosluk=2, dx=20)
k.C(cv, g, "100n", "+1V8_JET"); k.C(cv, g, "100n", "+3V3")
cv.metin("FAN (5 V, 4 uclu: GND, +5V, devir, PWM; Vision ile ayni): PWM Jetson'dan; Jetson kapaliyken 10k asagi cekme fani durdurur.", 30, 490)
g = Izgara(50, 530, sutun=10)
k.parca(cv, g, "Connector_Generic:Conn_01x04", "J", "Fan (PicoBlade)", {"Pin_1": "GND", "Pin_2": "+5V", "Pin_3": "FAN_TACH_K", "Pin_4": "FAN_PWM"},
        "Connector_Molex:Molex_PicoBlade_53047-0410_1x04_P1.25mm_Vertical", dx=8)
k.R(cv, g, "100R", "FAN_PWM_3V3", "FAN_PWM"); k.R(cv, g, "10k", "FAN_PWM", "GND")
k.R(cv, g, "10k", "+3V3", "FAN_TACH"); k.R(cv, g, "10k", "FAN_TACH_K", "FAN_TACH"); k.C(cv, g, "1n", "FAN_TACH")
k.C(cv, g, "10u 10V", "+5V", fp=C0805)
cv.yaz(os.path.join(BURASI, "cevre.kicad_sch"))

# --- Geniş bant radyo, ikinci Ethernet portu ---------------------------------------------
wb = Sema(k.P, "Pilot Pro - genis bant radyo modulu ve ikinci Ethernet portu (I210)", kagit="A0", tarih=k.T, ust=kok, ad="Genisbant", genel_etiket=True)
kok.alt_sayfa(wb, "genisbant.kicad_sch", 25.4, 101.6)
wb.metin("GENIS BANT RADYO MODULU (Microhard pMDDL2450 OEM, 2,4 GHz, 2x2 MIMO, 1 W): baglanti Radio kartindakinin aynisi (uretici kilavuzu, Tablo 3-3).", 30, 28)
wb.metin("Antenler modulun ustundeki iki U.FL'den kabloyla kasadaki SMA'lara gider. Modul yaklasik 7,5 W isi uretir: sogutucu sart.", 30, 34)
wb.metin("Modul Jetson'a Ethernet'ten baglidir (ayar ve video). Seri port yalnizca kurtarma icindir (0R + olcum noktalari). Sifirlama, ayar ve", 30, 40)
wb.metin("verici beslemesini kesme uclari guc islemcisinin I2C hattindaki kucuk genisleticidedir (PCA9536, adres 0x41); acilista hepsi bostadir.", 30, 46)
k.koy(wb, "operfly:pMDDL2450", "U", "pMDDL2450 OEM", 110, 150, {
    "Vcc": "+3V3", "VRF": "+5V_RF", "GND": "GND",
    "Serial_RxD": "WB_RXD_M", "Serial_TxD": "WB_TXD_M",
    "RESET": "WB_NRST", "CONFIG": "WB_CONFIG_N", "CPU_STATUS_LED": "WB_CPU_STATUS",
    "LED_RX": "WB_LED_RX", "LED_TX": "WB_LED_TX", "ETH0_LINK_LED": "WB_ETH_LINK",
    "TX_P0": "RETH_TXP", "TX_N0": "RETH_TXN", "RX_P0": "RETH_RXP", "RX_N0": "RETH_RXN", "ETH_BIAS": "RETH_BIAS"},
    "operfly_ayak:Microhard_pMDDL_OEM")
g = Izgara(50, 250, sutun=10)
for ag, n in (("+3V3", 2), ("+5V_RF", 2)):
    k.C(wb, g, "22u 16V", ag, fp=C1206)
    for _ in range(n):
        k.C(wb, g, "100n", ag)
k.C(wb, g, "100p", "+5V_RF")
g.satir()
k.R(wb, g, "0R", "WB_RXD", "WB_RXD_M"); k.R(wb, g, "0R", "WB_TXD", "WB_TXD_M")
k.olcum_noktasi(wb, g, "WB_RXD"); k.olcum_noktasi(wb, g, "WB_TXD")
k.R(wb, g, "10k", "+3V3", "WB_NRST"); k.R(wb, g, "10k", "+3V3", "WB_CONFIG_N")
k.olcum_noktasi(wb, g, "WB_CONFIG_N"); k.olcum_noktasi(wb, g, "WB_NRST")
g.satir()
for ag, ad in (("WB_CPU_STATUS", "mavi (modul)"), ("WB_LED_RX", "yesil (alis)"), ("WB_LED_TX", "kirmizi (veris)"), ("WB_ETH_LINK", "sari (Ethernet)")):
    k.R(wb, g, "1k", ag, ag + "_A"); k.iki(wb, g, "Device:LED", "D", "LED " + ad, "GND", ag + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(wb, g, "10k", ag, "GND")
g = Izgara(50, 370, sutun=10)
k.parca(wb, g, "Interface_Expansion:PCA9536D", "U", "PCA9536D", {"VDD": "+3V3", "VSS": "GND", "SCL": "PWR_SCL", "SDA": "PWR_SDA",
        "IO0": "WB_NRST", "IO1": "WB_CONFIG_N", "IO2": "WB_RF_OFF", "IO3": "WB_CPU_STATUS"}, "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", bosluk=2, dx=18)
k.C(wb, g, "100n", "+3V3")

wb.metin("5 V VERICI BESLEMESI (AP63201, +VSYS'ten; Radio kartindaki devre): verici kati ortalama 1,2 A, anlik 1,5 A ceker. Sifirlamada ACIK;", 30, 420)
wb.metin("WB_RF_OFF = 1 vericiyi susturur. Cikis = 0,8 V x (1 + 158k / 30k1) = 5,0 V. Modulun 3,3 V'u kartin 3,3 V rayindandir (0,5 A).", 30, 426)
g = Izgara(50, 465, sutun=12)
k.parca(wb, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+VSYS", "EN": "EN_RF", "GND": "GND", "SW": "SW_RF", "BST": "BST_RF", "FB": "FB_RF"}, TSOT6)
k.R(wb, g, "100k", "+VSYS", "EN_RF"); k.C(wb, g, "10u 50V", "+VSYS", fp=C1206); k.C(wb, g, "100n", "BST_RF", "SW_RF")
k.iki(wb, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_RF", "+5V_RF", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(wb, g, "22u 16V", "+5V_RF", fp=C1206); k.C(wb, g, "22u 16V", "+5V_RF", fp=C1206); k.bayrak(wb, g, "+5V_RF")
g.satir()
k.R(wb, g, "158k 1%", "+5V_RF", "FB_RF"); k.R(wb, g, "30k1 1%", "FB_RF", "GND"); k.C(wb, g, "100p", "+5V_RF", "FB_RF")
x, y = g.yer()
k.koy(wb, N7002[0], N7002[1], N7002[2], x, y, {"D": "EN_RF", "S": "GND", "G": "WB_RF_OFF"}, SOT23)
k.R(wb, g, "100k", "WB_RF_OFF", "GND"); k.olcum_noktasi(wb, g, "+5V_RF")

wb.metin("RADYO <-> JETSON ETHERNET BAGLANTISI: modulun 10/100 portu kendi trafosundan (uretici ornegi), ikinci Ethernet denetleyicisi de kendi", 420, 28)
wb.metin("trafosundan gecer; iki trafonun kablo taraflari kart uzerinde birlesir (kisa bir kablo baglantisinin esdegeri). Ciftler caprazdir:", 420, 34)
wb.metin("modulun gonderme cifti denetleyicinin alma ciftine (MDI1), alma cifti gonderme ciftine (MDI0). C ve D ciftleri kullanilmaz (100 Mbit).", 420, 40)
g = Izgara(440, 90, sutun=12)
k.parca(wb, g, "Transformer:PT61017PEL", "T", "PT61017PEL (10/100, 1:1)", {
    "TD+": "RETH_TXP", "TD-": "RETH_TXN", "C_TD": "RETH_CT", "RD+": "RETH_RXP", "RD-": "RETH_RXN", "C_RD": "RETH_CT",
    "TX+": "WB_MTX+", "TX-": "WB_MTX-", "C_TX": "RETH_CT_A", "RX+": "WB_MRX+", "RX-": "WB_MRX-", "C_RX": "RETH_CT_B"},
    "Transformer_SMD:Transformer_Ethernet_Bourns_PT61017PEL", bosluk=2, dx=25)
k.R(wb, g, "49R9 1%", "RETH_TXP", "RETH_TERM_TX"); k.R(wb, g, "49R9 1%", "RETH_TXN", "RETH_TERM_TX"); k.C(wb, g, "100n", "RETH_TERM_TX")
k.R(wb, g, "49R9 1%", "RETH_RXP", "RETH_TERM_RX"); k.R(wb, g, "49R9 1%", "RETH_RXN", "RETH_TERM_RX"); k.C(wb, g, "100n", "RETH_TERM_RX")
g.satir()
k.iki(wb, g, "Device:FerriteBead", "FB", "BLM18HD102SN1D", "RETH_BIAS", "RETH_CT", "Inductor_SMD:L_0603_1608Metric")
k.C(wb, g, "100n", "RETH_BIAS"); k.C(wb, g, "100n", "RETH_CT")
k.R(wb, g, "75R", "RETH_CT_A", "WB_BS"); k.R(wb, g, "75R", "RETH_CT_B", "WB_BS")

wb.metin("IKINCI ETHERNET PORTU (Intel I210-IT, Jetson PCIE1; Vision'daki kamera portu devresinin aynisi): besleme tam tumlesik (CTOP-CBOT 39 nF),", 420, 170)
wb.metin("RSET 4k99, 25 MHz kristal + 27 pF, ayar icin SPI flash. Kullanilmayan NC-SI, SMBus ve JTAG uclari uretici tablosundaki gibi cekilir.", 420, 176)
e, y0, V, GD = "E1", 290, "+3V3_JET", "GND"
ust = {4: "TDO", 5: "NRX1", 6: "NRX0", 8: "NTX1", 9: "NTX0", 16: "WAKE", 18: "TMS", 28: "DEVOFF", 29: "TDI", 34: "SMBC", 35: "SMBA", 36: "SMBD", 1: "PG"}
alt = {2: "NCLK", 3: "NCRS", 7: "NTXEN", 19: "TCK", 12: "NVM_SI"}
a = {10: V, 27: V, 41: V, 51: V, 64: V, 65: GD, 11: e + "_0V9", 32: e + "_0V9", 42: e + "_0V9", 59: e + "_0V9", 38: e + "_0V9",
     47: e + "_1V5", 56: e + "_1V5", 39: e + "_1V5", 37: e + "_CBOT", 40: e + "_CTOP", 48: e + "_RSET", 45: e + "_XO", 46: e + "_XI",
     13: e + "_NVM_SK", 14: e + "_NVM_SO", 15: e + "_NVM_CS", 17: e + "_RST_N", 20: e + "_PET_N", 21: e + "_PET_P", 23: e + "_PER_N", 24: e + "_PER_P",
     25: e + "_CLK_N", 26: e + "_CLK_P", 31: e + "_LED",
     58: e + "_MDI0_P", 57: e + "_MDI0_N", 55: e + "_MDI1_P", 54: e + "_MDI1_N", 53: e + "_MDI2_P", 52: e + "_MDI2_N", 50: e + "_MDI3_P", 49: e + "_MDI3_N"}
a.update({no: "%s_%s" % (e, ad) for no, ad in list(ust.items()) + list(alt.items())})
k.koy(wb, "Interface_Ethernet:WGI210AT", "U", "WGI210IT", 500, y0, {str(no): ag for no, ag in a.items()}, "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm")
g = Izgara(430, y0 + 75, sutun=22, dx=20)
for ad in ust.values():
    k.R(wb, g, "10k", V, "%s_%s" % (e, ad))
for ad in alt.values():
    k.R(wb, g, "10k", "%s_%s" % (e, ad), GD)
g.satir()
for _ in range(5):
    k.C(wb, g, "100n", V)
k.C(wb, g, "22u 10V", V, fp=C1206)
for _ in range(4):
    k.C(wb, g, "100n", e + "_0V9")
k.C(wb, g, "22u 6V3", e + "_0V9", fp=C0805)
for _ in range(2):
    k.C(wb, g, "100n", e + "_1V5")
k.C(wb, g, "22u 6V3", e + "_1V5", fp=C0805)
k.C(wb, g, "39n", e + "_CTOP", e + "_CBOT"); k.R(wb, g, "4k99 1%", e + "_RSET", GD)
g.satir()
k.koy(wb, "Device:Crystal_GND24", "Y", "25 MHz 30 ppm", *g.yer(), {"1": e + "_XI", "3": e + "_XO", "2": GD, "4": GD}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(wb, g, "27p", e + "_XI"); k.C(wb, g, "27p", e + "_XO")
k.C(wb, g, "220n", e + "_PET_P", e + "_PET_C_P"); k.C(wb, g, "220n", e + "_PET_N", e + "_PET_C_N")
k.C(wb, g, "220n", "J_PCIE1_TX_P", e + "_PER_P"); k.C(wb, g, "220n", "J_PCIE1_TX_N", e + "_PER_N"); k.R(wb, g, "0R", e + "_CLKREQ_N", GD)
k.parca(wb, g, "Memory_Flash:W25Q32JVSS", "U", "W25Q16JVSSIQ", {"~{CS}": e + "_NVM_CS", "CLK": e + "_NVM_SK", "DI/IO_{0}": e + "_NVM_SI", "DO/IO_{1}": e + "_NVM_SO",
        "~{WP}/IO_{2}": e + "_NVM_WP", "~{HOLD}/~{RESET}/IO_{3}": e + "_NVM_HOLD", "VCC": V, "GND": GD}, "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", bosluk=2, dx=18)
k.R(wb, g, "10k", V, e + "_NVM_WP"); k.R(wb, g, "10k", V, e + "_NVM_HOLD"); k.C(wb, g, "100n", V)
k.iki(wb, g, "Device:LED", "D", "LED yesil (baglanti)", e + "_LED", e + "_LED_A", "LED_SMD:LED_0603_1608Metric"); k.R(wb, g, "1k", V, e + "_LED_A")
tr = {}
kablo = {"A": ("WB_MRX+", "WB_MRX-"), "B": ("WB_MTX+", "WB_MTX-")}
for c, i, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", range(4), ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
    tr.update({str(cp): "E1_MDI%d_P" % i, str(cm): "E1_MDI%d_N" % i, str(cc): "E1_CT_%s" % c, str(kc_): "E1_KCT_%s" % c})
    if c in kablo:
        tr.update({str(kp_): kablo[c][0], str(km_): kablo[c][1]})
k.koy(wb, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", 690, y0, tr, "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13")
g = Izgara(760, y0 - 30, sutun=9, dx=24)
for c in "ABCD":
    k.C(wb, g, "100n", "E1_CT_%s" % c)
for c in "ABCD":
    k.R(wb, g, "75R", "E1_KCT_%s" % c, "WB_BS")
k.C(wb, g, "1n 2kV", "WB_BS", fp=C1206)
wb.yaz(os.path.join(BURASI, "genisbant.kicad_sch"))

# --- Ekran: goruntu cikisi (HDMI), panel beslemesi, parlaklik --------------------------------
ek = Sema(k.P, "Pilot Pro - ekran: HDMI, panel beslemesi, parlaklik", kagit="A1", tarih=k.T, ust=kok, ad="Ekran", genel_etiket=True)
kok.alt_sayfa(ek, "ekran.kicad_sch", 101.6, 101.6)
ek.metin("EKRAN ARAYUZU: kart belirli bir panele bagli DEGILDIR. Hedef en yuksek parlaklikli (nit), dis ortamda okunan 10 inc dokunmatik paneldir;", 30, 28)
ek.metin("goruntu HDMI ile, besleme 12 V ile, dokunmatik USB ile (Cevre sayfasi), parlaklik PWM ile verilir. Boylece panel degisince kart degismez.", 30, 34)
ek.metin("GORUNTU CIKISI (HDMI; Jetson DP1 uclari HDMI kipinde): uretici tasarim kilavuzu (DG-10931, bolum 9) ve acik kaynakli bir tasiyici kartin", 30, 46)
ek.metin("uretilmis devresi esas alindi. Esleme: TXD0 = veri 2, TXD1 = veri 1, TXD2 = veri 0, TXD3 = saat; AUX_P = SCL, AUX_N = SDA.", 30, 52)
ek.metin("Her hatta 100 nF seri kondansator, 499R asagi cekme (ortak transistorle, yalniz Jetson acikken), 0R seri direnc (gerekirse 5R1), ESD dizisi.", 30, 58)
TMDS = (("D2", "DP1_TXD0"), ("D1", "DP1_TXD1"), ("D0", "DP1_TXD2"), ("CK", "DP1_TXD3"))
g = Izgara(50, 100, sutun=16, dx=24)
for ad, _ in TMDS:
    for s_ in "PN":
        k.C(ek, g, "100n", "HDMI_%s_J_%s" % (ad, s_), "HDMI_%s_C_%s" % (ad, s_))
for ad, _ in TMDS:
    for s_ in "PN":
        k.R(ek, g, "499R 1%", "HDMI_%s_C_%s" % (ad, s_), "HDMI_RPD")
g.satir()
for ad, _ in TMDS:
    for s_ in "PN":
        k.R(ek, g, "0R", "HDMI_%s_C_%s" % (ad, s_), "HDMI_%s_K_%s" % (ad, s_))
x, y = g.yer()
k.koy(ek, "Transistor_FET:AO3400A", "Q", "AO3400A", x, y, {"D": "HDMI_RPD", "S": "GND", "G": "+3V3_JET"}, SOT23)
g = Izgara(70, 215, sutun=6, dx=75)
k.parca(ek, g, "Power_Protection:TPD4E05U06DQA", "D", "TPD4E05U06DQA", {"D1+": "HDMI_D2_K_P", "D1-": "HDMI_D2_K_N", "D2+": "HDMI_D1_K_P", "D2-": "HDMI_D1_K_N", "GND": "GND"},
        "Package_SON:USON-10_2.5x1.0mm_P0.5mm", bosluk=0, dx=18)
k.parca(ek, g, "Power_Protection:TPD4E05U06DQA", "D", "TPD4E05U06DQA", {"D1+": "HDMI_D0_K_P", "D1-": "HDMI_D0_K_N", "D2+": "HDMI_CK_K_P", "D2-": "HDMI_CK_K_N", "GND": "GND"},
        "Package_SON:USON-10_2.5x1.0mm_P0.5mm", bosluk=0, dx=18)
k.parca(ek, g, "Power_Protection:TPD4E05U06DQA", "D", "TPD4E05U06DQA", {"D1+": "HDMI_SCL_5V", "D1-": "HDMI_SDA_5V", "D2+": "HDMI_HPD_K", "GND": "GND"},
        "Package_SON:USON-10_2.5x1.0mm_P0.5mm", bosluk=0, dx=18)

ek.metin("DDC (panelin kimlik bilgisi) ve HPD (panel takili): Jetson uclari 5 V'a dayanmaz -> seviye cevirici sart (uretici notu).", 30, 262)
ek.metin("DDC: transistorlu iki yonlu cevirici; panel tarafi 1k8 ile 5 V'a, Jetson tarafi 10k ile 3,3 V'a cekili. HPD: tersleyen transistor,", 30, 268)
ek.metin("Jetson tarafi 10k ile 1,8 V'a cekili (panel takiliyken hat DUSUK; ureticinin kendi kartindaki gibi). CEC kullanilmaz (uclar bos).", 30, 274)
g = Izgara(50, 315, sutun=14)
for h in ("SCL", "SDA"):
    k.R(ek, g, "10k", "+3V3_JET", "HDMI_%s_3V3" % h)
    x, y = g.yer()
    k.koy(ek, N7002[0], N7002[1], N7002[2], x, y, {"G": "+3V3_JET", "S": "HDMI_%s_3V3" % h, "D": "HDMI_%s_5V" % h}, SOT23)
    k.R(ek, g, "1k8", "+5V_HDMI", "HDMI_%s_5V" % h)
k.R(ek, g, "1k", "HDMI_HPD_K", "HDMI_HPD_G"); k.R(ek, g, "100k", "HDMI_HPD_G", "GND")
x, y = g.yer()
k.koy(ek, N7002[0], N7002[1], N7002[2], x, y, {"G": "HDMI_HPD_G", "S": "GND", "D": "HDMI_HPD_N_1V8"}, SOT23)
k.R(ek, g, "10k", "+1V8_JET", "HDMI_HPD_N_1V8"); k.olcum_noktasi(ek, g, "HDMI_HPD_N_1V8")
g.satir()
k.parca(ek, g, "Power_Management:TPS2051CDBV", "U", "TPS2051CDBV", {"IN": "+5V", "GND": "GND", "EN": "JET_RUN", "~{FLT}": "HDMI_5V_FLT_N", "OUT": "+5V_HDMI"},
        "Package_TO_SOT_SMD:SOT-23-5", bosluk=1, dx=14)
k.C(ek, g, "1u", "+5V"); k.C(ek, g, "10u 10V", "+5V_HDMI", fp=C0805); k.C(ek, g, "100n", "+5V_HDMI")
k.R(ek, g, "10k", "+3V3", "HDMI_5V_FLT_N"); k.olcum_noktasi(ek, g, "HDMI_5V_FLT_N")

ek.metin("HDMI KONNEKTORU (A tipi, kasa icinde): panelin surucu kartina kisa bir HDMI kablosuyla baglanir. 5 V ucu 0,5 A sinirlidir (TPS2051C).", 420, 46)
H = {"+5V": "+5V_HDMI", "GND": "GND", "SH": "GND", "D2S": "GND", "D1S": "GND", "D0S": "GND", "CKS": "GND",
     "SCL": "HDMI_SCL_5V", "SDA": "HDMI_SDA_5V", "HPD": "HDMI_HPD_K"}
for ad, _ in TMDS:
    H[ad + "+"] = "HDMI_%s_K_P" % ad
    H[ad + "-"] = "HDMI_%s_K_N" % ad
k.koy(ek, "Connector:HDMI_A", "J", "HDMI-A (panel)", 500, 120, H, "Connector_Video:HDMI_A_Molex_208658-1001_Horizontal")

ek.metin("PANEL BESLEMESI (TPS54560B, +VSYS'ten 12 V, 3 A = 36 W): 2000 nit sinifi bir panele (tahmini 20-25 W) yetecek sekilde boyutlandi.", 420, 262)
ek.metin("Cikis = 0,8 V x (1 + 143k / 10k2) = 12,0 V; 400 kHz. Batarya 12,5 V'un altina inince cikis bataryayi izler (yaklasik 0,5 V altinda;", 420, 268)
ek.metin("regulator tam acik calisir). Yalnizca Jetson acikken calisir (tasiyici 3,3 V'u gelince). Parlaklik: Jetson GPIO13 (PWM) -> seviye cevirici.", 420, 274)
g = Izgara(440, 320, sutun=16, dx=24)
k.parca(ek, g, "Regulator_Switching:TPS54560BDDA", "U", "TPS54560BDDAR", {"VIN": "+VSYS", "EN": "PNL_EN", "RT/CLK": "PNL_RT", "FB": "PNL_FB",
        "COMP": "PNL_COMP", "BOOT": "PNL_BOOT", "SW": "PNL_SW", "GND": "GND"}, "Package_SO:Texas_R-PDSO-G8_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias", bosluk=2, dx=22)
k.C(ek, g, "10u 50V", "+VSYS", fp=C1206); k.C(ek, g, "10u 50V", "+VSYS", fp=C1206); k.C(ek, g, "100n 50V", "+VSYS", fp=C0603)
k.R(ek, g, "243k 1%", "PNL_RT", "GND"); k.R(ek, g, "13k7", "PNL_COMP", "PNL_COMP_RC"); k.C(ek, g, "10n", "PNL_COMP_RC"); k.C(ek, g, "56p", "PNL_COMP")
k.C(ek, g, "100n 25V", "PNL_BOOT", "PNL_SW", fp=C0603)
k.iki(ek, g, "Device:D_Schottky", "D", "PDS760 (60 V, 7 A)", "PNL_SW", "GND", "Diode_SMD:D_PowerDI-5")
k.iki(ek, g, "Device:L", "L", "10u XAL7070-103", "PNL_SW", "+12V_PNL", "Inductor_SMD:L_Coilcraft_XAL7070-XXX")
g.satir()
for _ in range(4):
    k.C(ek, g, "22u 25V", "+12V_PNL", fp=C1210)
k.R(ek, g, "143k 1%", "+12V_PNL", "PNL_FB"); k.R(ek, g, "10k2 1%", "PNL_FB", "GND")
k.R(ek, g, "10k", "+3V3_JET", "PNL_EN"); k.R(ek, g, "100k", "PNL_EN", "GND")
k.olcum_noktasi(ek, g, "+12V_PNL")
k.parca(ek, g, "Connector_Generic:Conn_01x02", "J", "Panel beslemesi 12 V (Micro-Fit)", {"Pin_1": "+12V_PNL", "Pin_2": "GND"},
        "Connector_Molex:Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal", dx=8)
g.satir()
k.R(ek, g, "100R", "BL_PWM_3V3", "PNL_PWM"); k.R(ek, g, "100k", "PNL_PWM", "GND"); k.R(ek, g, "1k", "+3V3_JET", "PNL_ON")
k.parca(ek, g, "Connector_Generic_MountingPin:Conn_01x03_MountingPin", "J", "Panel denetimi (ac, PWM, GND)", {"Pin_1": "PNL_ON", "Pin_2": "PNL_PWM", "Pin_3": "GND",
        "MountPin": "GND"}, "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
ek.yaz(os.path.join(BURASI, "ekran.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_pilotpro.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gc, rd, jt, cv, wb, ek], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_pilotpro (kok + 7 sayfa)")
