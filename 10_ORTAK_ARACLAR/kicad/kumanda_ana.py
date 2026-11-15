"""Kumanda ana kartlarının ortak bölümü: Pilot 12 ve Pilot T aynı devreyi kullanır (Pilot T buna ekran sayfası ekler).

İçerik: tek hücreli Li-ion batarya girişi, USB Type-C'den şarj (güç yolu), batarya ölçer, güç açma/tutma,
3,3 V ve radyo beslemesi, kumanda radyo modülü (RFD900ux-SMT) ve antenleri, sesli uyarıcı, giriş kartı bağlantısı.
Kart işlemci taşımaz: işlemci ve güvenli eleman giriş kartındadır (01_DONANIM/KUMANDA_GIRIS).
Giriş kartıyla bağlantı: 13_DOKUMANTASYON/KUMANDA_ARAYUZU.md (20 kontaklı yassı kablo).
Devre değerleri üretici veri sayfalarındandır: BQ24075 (SLUS810N), bq27441-G1 (SLUSBH1C), TPS63001 (SLVS520C),
TPS61230 (SLVSAQ2C), LMV393 (SLCS136V), RFD900ux/RFD868ux (V1.3).
"""
import os

from kart import C0603, C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: F401
from sema_uret import Sema

AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
KUTUPHANELER = {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI}
N7002 = ("Transistor_FET:2N7002", "Q", "2N7002")
SOT23 = "Package_TO_SOT_SMD:SOT-23"


def ana_kart(proje, ad, kod, klasor, burasi, tarih="2026-11-15"):
    """Kök sayfayı ve iki ortak sayfayı (güç, radyo) üretir, alt sayfaları yazar. Döndürür: (Kart, kök Sema, [alt sayfalar]).
    Kök sayfayı ve kütüphane tablolarını çağıran yazar (önce kendi sayfalarını ekleyebilir)."""
    k = Kart(proje, tarih)
    kok = Sema(k.P, "Operfly " + ad, kagit="A3", tarih=k.T)
    kok.metin("Operfly %s - kumanda ana karti (%s)" % (ad, kod), 25.4, 25.4, 3.0)
    kok.metin("Sematik betikle uretilir: 01_DONANIM/%s/kicad/uret.py. Islemci giris kartindadir." % klasor, 25.4, 33.02, 1.6)

    # --- Güç: batarya, şarj, ölçer, USB, güç açma/tutma, 3,3 V --------------------
    gc = Sema(k.P, ad + " - batarya, sarj, USB, guc acma/tutma, 3,3 V", kagit="A1", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
    kok.alt_sayfa(gc, "guc.kicad_sch", 25.4, 50.8)

    gc.metin("USB TYPE-C: sarj girisi + islemcinin USB'si (yassi kablodan giris kartina). CC uclarinda 5,1 k: kart tuketicidir.", 30, 28)
    g = Izgara(50, 75, sutun=12)
    k.parca(gc, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C", {"VBUS": "VBUS_USB", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2",
            "D+": "USB_DP", "D-": "USB_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
    x, y = g.yer(); g.yer()
    k.koy(gc, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "5": "VBUS_USB", "2": "GND"},
          "Package_TO_SOT_SMD:SOT-666")
    k.R(gc, g, "5k1 1%", "USB_CC1", "GND"); k.R(gc, g, "5k1 1%", "USB_CC2", "GND"); k.C(gc, g, "4u7 25V", "VBUS_USB", fp=C0805)
    k.bayrak(gc, g, "VBUS_USB"); k.bayrak(gc, g, "GND")

    gc.metin("KAYNAK AKIMI ALGILAMA (LMV393): Type-C kaynagi verebildigi akimi CC gerilimiyle bildirir (standart < 0,61 V; 1,5 A > 0,70 V).", 30, 140)
    gc.metin("Esik 0,66 V. Standart kaynakta sarj entegresi 0,5 A giris sinirinda (EN2=0, EN1=1), 1,5 A / 3 A bildiren kaynakta", 30, 146)
    gc.metin("direncle ayarli 1,36 A sinirinda (EN2=1, EN1=0) calisir. HICUR_N: 0 = kaynak en az 1,5 A verebiliyor.", 30, 152)
    g = Izgara(50, 190, sutun=12)
    x, y = g.yer(); g.yer(); g.yer(); g.yer(); g.yer(); g.yer(); g.yer()
    k.koy(gc, "Comparator:LMV393", "U", "LMV393", x + 10, y, {"2": "CC1_F", "3": "CC_REF", "1": "HICUR_N", "6": "CC2_F", "5": "CC_REF", "7": "HICUR_N", "8": "+3V3", "4": "GND"},
          "Package_SO:TSSOP-8_4.4x3mm_P0.65mm")
    g.satir()
    k.R(gc, g, "10k", "USB_CC1", "CC1_F"); k.R(gc, g, "10k", "USB_CC2", "CC2_F")
    k.R(gc, g, "40k2 1%", "+3V3", "CC_REF"); k.R(gc, g, "10k 1%", "CC_REF", "GND"); k.C(gc, g, "100n", "CC_REF"); k.C(gc, g, "100n", "+3V3")
    k.R(gc, g, "100k", "+3V3", "HICUR_N"); k.R(gc, g, "100k", "+3V3", "CHG_EN2")
    x, y = g.yer()
    k.koy(gc, N7002[0], N7002[1], N7002[2], x, y, {"D": "CHG_EN2", "S": "GND", "G": "HICUR_N"}, SOT23)

    gc.metin("BATARYA (tek hucreli Li-ion paket, koruma devreli, 10 k NTC'li): 3 kontak = +, NTC, -. Olcer icin 10 mOhm seri direnc.", 330, 28)
    g = Izgara(350, 75, sutun=12)
    k.parca(gc, g, "Connector_Generic:Conn_01x03", "J", "Batarya (JST-XH)", {"Pin_1": "+BATT", "Pin_2": "BAT_NTC", "Pin_3": "GND"},
            "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical", dx=8)
    k.R(gc, g, "10m 1% 1W", "+BATT", "+BAT_CHG", fp="Resistor_SMD:R_1206_3216Metric")
    k.C(gc, g, "10u 10V", "+BATT", fp=C0805); k.bayrak(gc, g, "+BATT")
    k.R(gc, g, "0R", "BAT_NTC", "CHG_TS"); k.R(gc, g, "10k", "CHG_TS", "GND", dnp=True)

    gc.metin("SARJ ve GUC YOLU (BQ24075): USB varken sistemi USB'den besler ve bataryayi sarj eder; USB yokken bataryadan besler.", 330, 120)
    gc.metin("Sarj akimi 890 / 887R = 1,0 A; giris siniri 1610 / 1k18 = 1,36 A; guvenlik zamanlayicisi 10 x 48 s x 68 = 9 saat.", 330, 126)
    gc.metin("SYSOFF = 1 bataryayi sistemden ayirir (kapali durum). CHG isigi sarj surerken yanar.", 330, 132)
    g = Izgara(350, 175, sutun=12)
    k.parca(gc, g, "Battery_Management:BQ24075RGT", "U", "BQ24075RGT", {
        "IN": "VBUS_USB", "BAT": "+BAT_CHG", "OUT": "+SYS", "VSS": "GND", "~{CE}": "GND", "EN1": "HICUR_N", "EN2": "CHG_EN2",
        "TS": "CHG_TS", "TMR": "CHG_TMR", "ILIM": "CHG_ILIM", "ISET": "CHG_ISET", "SYSOFF": "SYSOFF", "~{CHG}": "CHG_LED_K"},
        "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm", bosluk=2, dx=20)
    k.R(gc, g, "887R 1%", "CHG_ISET", "GND"); k.R(gc, g, "1k18 1%", "CHG_ILIM", "GND"); k.R(gc, g, "68k 1%", "CHG_TMR", "GND")
    k.C(gc, g, "10u 10V", "+BAT_CHG", fp=C0805); k.C(gc, g, "22u 10V", "+SYS", fp=C1206); k.C(gc, g, "100n", "+SYS")
    k.iki(gc, g, "Device:LED", "D", "LED turuncu (sarj)", "CHG_LED_K", "CHG_LED_A", "LED_SMD:LED_0603_1608Metric"); k.R(gc, g, "1k5", "+SYS", "CHG_LED_A")

    gc.metin("BATARYA OLCER (bq27441-G1A): kalan kapasiteyi ve gerilimi I2C'den verir; GPOUT -> ALERT_N. Yukari cekmeler giris kartinda.", 330, 230)
    g = Izgara(350, 275, sutun=12)
    k.parca(gc, g, "Battery_Management:BQ27441DRZR-G1A", "U", "BQ27441DRZR-G1A", {
        "BAT": "+BATT", "SRP": "+BATT", "SRN": "+BAT_CHG", "V_{DD}": "GAUGE_VDD", "V_{SS}": "GND", "PAD": "GND",
        "SDA": "I2C_SDA", "SCL": "I2C_SCL", "GPOUT": "ALERT_N", "BIN": "GAUGE_BIN"}, "Package_SON:Texas_S-PDSO-N12", bosluk=2, dx=22)
    k.C(gc, g, "1u", "+BATT"); k.C(gc, g, "470n", "GAUGE_VDD"); k.R(gc, g, "10k", "GAUGE_BIN", "GND")

    gc.metin("GUC ACMA / TUTMA: kapaliyken SYSOFF ic direncle yuksektir. Dugme SYSOFF'u diyot uzerinden sifira ceker -> sistem acilir;", 330, 330)
    gc.metin("islemci PWR_HOLD = 1 ile tutar, 0 yapinca kapanir. USB takiliyken SYSOFF kendiliginden sifirdadir (sarj islemciye bagli degil).", 330, 336)
    gc.metin("Cift diyot dugmeyi iki hatta ayri ayri baglar: kapaliyken giris kartindaki yukari cekme SYSOFF'u etkilemez.", 330, 342)
    g = Izgara(350, 380, sutun=12)
    k.parca(gc, g, "Connector_Generic_MountingPin:Conn_01x02_MountingPin", "J", "Guc dugmesi", {"Pin_1": "PWR_BTN", "Pin_2": "GND", "MountPin": "GND"},
            "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal", dx=8)
    x, y = g.yer()
    k.koy(gc, "Diode:BAT54C", "D", "BAT54C", x, y, {"1": "SYSOFF", "2": "PWR_BTN_N", "3": "PWR_BTN"}, SOT23)
    k.C(gc, g, "100n", "PWR_BTN")
    x, y = g.yer()
    k.koy(gc, N7002[0], N7002[1], N7002[2], x, y, {"D": "SYSOFF", "S": "GND", "G": "PWR_HOLD"}, SOT23)
    k.R(gc, g, "100k", "PWR_HOLD", "GND")
    x, y = g.yer()
    k.koy(gc, N7002[0], N7002[1], N7002[2], x, y, {"D": "SYSOFF", "S": "GND", "G": "VBUS_SENS"}, SOT23)
    k.R(gc, g, "100k", "VBUS_USB", "VBUS_SENS"); k.R(gc, g, "220k", "VBUS_SENS", "GND")
    k.olcum_noktasi(gc, g, "SYSOFF")

    gc.metin("3,3 V (TPS63001, alcaltan-yukselten, sabit 3,3 V): giris 3,0-5,5 V araliginin tamaminda calisir. Sabit frekans (PS = 1).", 30, 270)
    g = Izgara(50, 310, sutun=12)
    k.parca(gc, g, "Regulator_Switching:TPS63001", "U", "TPS63001DRC", {
        "VIN": "+SYS", "VINA": "VINA_3V3", "EN": "+SYS", "PS/SYNC": "+SYS", "L1": "L1_3V3", "L2": "L2_3V3", "VOUT": "+3V3", "FB": "+3V3",
        "GND": "GND", "PGND": "GND"}, "Package_SON:Texas_DRC0010J_ThermalVias", bosluk=2, dx=18)
    k.iki(gc, g, "Device:L", "L", "2u2 XAL4020-222", "L1_3V3", "L2_3V3", "Inductor_SMD:L_Coilcraft_XAL4020-XXX")
    k.C(gc, g, "10u 10V", "+SYS", fp=C0805); k.R(gc, g, "100R", "+SYS", "VINA_3V3"); k.C(gc, g, "100n", "VINA_3V3")
    k.C(gc, g, "10u 10V", "+3V3", fp=C0805); k.C(gc, g, "10u 10V", "+3V3", fp=C0805)
    k.bayrak(gc, g, "VINA_3V3")

    gc.metin("SESLI UYARICI (piezo): islemcinin BUZZER cikisi transistorle surer; 1 k paralel direnc piezoyu bosaltir.", 30, 370)
    g = Izgara(50, 410, sutun=12)
    x, y = g.yer(); g.yer()
    k.koy(gc, "Device:Buzzer", "BZ", "PKLCS1212E4001", x + 5, y, {"+": "+SYS", "-": "BUZZER_K"}, "Buzzer_Beeper:Buzzer_Murata_PKLCS1212E")
    k.R(gc, g, "1k", "+SYS", "BUZZER_K")
    x, y = g.yer()
    k.koy(gc, N7002[0], N7002[1], N7002[2], x, y, {"D": "BUZZER_K", "S": "GND", "G": "BUZZER"}, SOT23)
    k.R(gc, g, "100k", "BUZZER", "GND")
    gc.yaz(os.path.join(burasi, "guc.kicad_sch"))

    # --- Radyo: besleme, modül, antenler, giriş kartı bağlantısı -------------------
    rd = Sema(k.P, ad + " - kumanda radyosu, radyo beslemesi, giris karti baglantisi", kagit="A2", tarih=k.T, ust=kok, ad="Radyo", genel_etiket=True)
    kok.alt_sayfa(rd, "radyo.kicad_sch", 101.6, 50.8)
    rd.metin("KUMANDA RADYO MODULU (RFD900ux-SMT; 868 MHz icin RFD868ux-SMT). Baglanti RX kartindakinin aynisi:", 30, 28)
    rd.metin("islemciden gelen hatlarda 470R, SWO ucu yazilim yukleme kipi icin islemcide (RADIO_BOOT_N).", 30, 34)
    k.koy(rd, "operfly:RFD900ux-SMT", "U", "RFD900ux-SMT (secenek: RFD868ux-SMT)", 100, 90, {
        "+5V": "+5V_RADIO", "GND": "GND", "RX": "RADIO_RX_M", "TX": "RADIO_TXD", "RTS": "RADIO_RTS", "CTS": "RADIO_CTS_M",
        "SWO": "RADIO_SWO", "ANT1": "RADIO_ANT1", "ANT2": "RADIO_ANT2", "+3V3_OUT": "RADIO_3V3"}, "operfly_ayak:RFDesign_RFD900ux-SMT")
    g = Izgara(50, 155, sutun=9)
    for a, b in (("RADIO_RXD", "RADIO_RX_M"), ("RADIO_CTS", "RADIO_CTS_M"), ("RADIO_BOOT_N", "RADIO_SWO")):
        k.R(rd, g, "470R", a, b)
    k.C(rd, g, "22u 10V", "+5V_RADIO", fp=C1206); k.C(rd, g, "100n", "+5V_RADIO"); k.C(rd, g, "100p", "+5V_RADIO")
    for ag in ("RADIO_SWO", "RADIO_3V3", "RADIO_TXD"):
        k.olcum_noktasi(rd, g, ag)
    g.satir()
    SMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
    for i in (1, 2):
        x, y = g.yer(); g.yer()
        k.koy(rd, "Connector:Conn_Coaxial", "J", "ANT %d (SMA)" % i, x + 5, y, {"In": "RADIO_ANT%d" % i, "Ext": "GND"}, SMA)

    rd.metin("RADYO BESLEMESI (TPS61230, yukselten): +SYS (3,0-5,5 V) -> 5,2 V. Modul verirken 1 A tepe ceker; entegre 3,3 V giristen 2,1 A verebilir.", 270, 28)
    rd.metin("Cikis = 1,0 V x (1 + 422k / 100k) = 5,22 V. Giris cikistan yuksekse (USB'de) entegre girisi dogrudan cikisa aktarir (en cok 5,5 V).", 270, 34)
    rd.metin("Besleme sifirlamada ACIKTIR; islemci RADIO_OFF = 1 ile keser. Devre ureticinin 5 V ornek devresidir.", 270, 40)
    g = Izgara(290, 85, sutun=9)
    k.parca(rd, g, "Regulator_Switching:TPS61230DRC", "U", "TPS61230DRC", {
        "VIN": "+SYS", "EN": "EN_RADIO", "SW": "SW_RADIO", "VOUT": "+5V_RADIO", "FB": "FB_RADIO", "SS": "SS_RADIO", "GND": "GND"},
        "Package_SON:Texas_S-PVSON-N10_ThermalVias", bosluk=2, dx=16)
    k.iki(rd, g, "Device:L", "L", "1u0 XAL4020-102", "+SYS", "SW_RADIO", "Inductor_SMD:L_Coilcraft_XAL4020-XXX")
    k.C(rd, g, "22u 10V", "+SYS", fp=C1206); k.C(rd, g, "10n", "SS_RADIO")
    for _ in range(3):
        k.C(rd, g, "22u 10V", "+5V_RADIO", fp=C1206)
    g.satir()
    k.R(rd, g, "422k 1%", "+5V_RADIO", "FB_RADIO"); k.R(rd, g, "100k 1%", "FB_RADIO", "GND")
    k.R(rd, g, "100k", "+SYS", "EN_RADIO")
    x, y = g.yer()
    k.koy(rd, N7002[0], N7002[1], N7002[2], x, y, {"D": "EN_RADIO", "S": "GND", "G": "RADIO_OFF"}, SOT23)
    k.R(rd, g, "100k", "RADIO_OFF", "GND")

    rd.metin("GIRIS KARTI BAGLANTISI (20 kontakli yassi kablo): uc sirasi 13_DOKUMANTASYON/KUMANDA_ARAYUZU.md ile birebir.", 270, 170)
    ANA = ["GND", "+3V3", "+3V3", "GND", "RADIO_RXD", "RADIO_TXD", "RADIO_CTS", "RADIO_RTS", "RADIO_OFF", "RADIO_BOOT_N",
           "GND", "USB_DM", "USB_DP", "GND", "I2C_SCL", "I2C_SDA", "ALERT_N", "PWR_BTN_N", "PWR_HOLD", "BUZZER"]
    ag = {"Pin_%d" % (i + 1): a for i, a in enumerate(ANA)}
    ag["MountPin"] = "GND"
    k.koy(rd, "Connector_Generic_MountingPin:Conn_01x20_MountingPin", "J", "Giris karti (FFC 20)", 300, 235, ag,
          "Connector_FFC-FPC:Hirose_FH12-20S-0.5SH_1x20-1MP_P0.50mm_Horizontal")
    rd.yaz(os.path.join(burasi, "radyo.kicad_sch"))
    return k, kok, [gc, rd]
