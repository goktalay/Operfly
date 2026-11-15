"""Operfly Ground Radio (yer radyosu) şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py YER_RADYO operfly_groundradio`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + geniş bant radyo modülü (Radio kartındaki devre; ek olarak modülün ikinci Ethernet portu) +
kumanda radyo modülü (RX kartındaki devre) + dış besleme girişi + dört omurga portu (yer tarafının dağıtım noktası).
Modüllerin uç sırası ve çevre devresi üretici belgelerindendir: pMDDL Operating Manual (bölüm 3.1 ve Ek C),
RFD900ux/RFD868ux Data Sheet V1.3. İşlemci pinleri KiCad pin verisindeki alternatif işlevlerle denetlendi.
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
FB0603 = "Inductor_SMD:L_0603_1608Metric"
TSOT6 = "Package_TO_SOT_SMD:TSOT-23-6"
N7002 = ("Transistor_FET:2N7002", "Q", "2N7002")
SOT23 = "Package_TO_SOT_SMD:SOT-23"
GECKO = "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical"
k = Kart("operfly_groundradio", "2026-11-15")
kok = Sema(k.P, "Operfly Ground Radio", kagit="A3", tarih=k.T)
kok.metin("Operfly Ground Radio - yer radyosu (OPFGRD)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/YER_RADYO/kicad/uret.py.", 25.4, 33.02, 1.6)

EK = {"PA2": "KUM_RXD", "PA3": "KUM_TXD",                 # USART2_TX -> kumanda modulu RX, USART2_RX <- modul TX
      "PA1": "KUM_CTS", "PA0": "KUM_RTS",                 # USART2_RTS -> modul CTS, USART2_CTS <- modul RTS
      "PA4": "KUM_OFF",                                   # 1: kumanda modulu beslemesi kapali (sifirlamada acik)
      "PB0": "KUM_BOOT_N",                                # 0 iken besleme acilirsa modul yazilim yukleme kipine girer
      "PA5": "KUM_VSENS",                                 # ADC1_IN5: kumanda modulu besleme gerilimi / 2
      "PB6": "WB_RXD", "PB7": "WB_TXD",                   # USART1_TX -> genis bant modul Serial RxD, USART1_RX <- Serial TxD
      "PB3": "WB_RTS", "PB4": "WB_CTS",                   # USART1_RTS -> modul RTS (giris), USART1_CTS <- modul CTS (cikis)
      "PC6": "WB_NRST", "PC7": "WB_CONFIG_N",             # acik kollektor: modulu sifirlar / fabrika ayari ve kurtarma kipi
      "PA7": "WB_RF_OFF",                                 # 1: verici katinin 5 V beslemesi kapali (sifirlamada acik)
      "PA8": "WB_CPU_STATUS",                             # modulun "calisiyor" cikisi
      "PB1": "WB_VRF_SENS",                               # ADC1_IN9: verici besleme gerilimi / 2
      "PA6": "VEXT_SENS"}                                 # ADC1_IN6: dis besleme girisi / 11 (Base ile ayni uc)
# besleme="kart": 1. portun 12 V ucu +12V_BUS'a cikar; kart +12V'u ortak baradan kendi diyoduyla uretir (Guc sayfasi).
# sonlandirma=True: yer tarafinda yildizin merkezi bu karttir (aracta Hub'in yaptigi is).
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, ethernet=2, ldo33=False, besleme="kart", sonlandirma=True)

# --- Geniş bant radyo: modül, seri arayüz, ışıklar, iki Ethernet portu, beslemeler -----------
rd = Sema(k.P, "Ground Radio - genis bant radyo, iki Ethernet portu", kagit="A1", tarih=k.T, ust=kok, ad="Genisbant", genel_etiket=True)
kok.alt_sayfa(rd, "genisbant.kicad_sch", 101.6, 50.8)
rd.metin("GENIS BANT RADYO MODULU (Microhard pMDDL2450 OEM, 2,4 GHz, 2x2 MIMO, 1 W): Radio kartindaki devrenin aynisi (uretici kilavuzu, Tablo 3-3).", 30, 28)
rd.metin("Antenler modulun ustundeki iki U.FL konnektorden kabloyla kasadaki SMA'lara gider; kartta RF hatti yoktur.", 30, 34)
rd.metin("Fark: modulun IKINCI Ethernet portu (WAN) da kullanilir; yazilimla LAN'a koprulenir ve ikinci bir yer cihazina gider.", 30, 40)
rd.metin("Modul yaklasik 7,5 W isi uretir: alt toprak duzlemi karta lehimlenir, ustune sogutucu konur (uretici sarti).", 30, 46)
k.koy(rd, "operfly:pMDDL2450", "U", "pMDDL2450 OEM", 110, 150, {
    "Vcc": "+3V3", "VRF": "+5V_RF", "GND": "GND",
    "Serial_RxD": "WB_RXD_M", "Serial_TxD": "WB_TXD_M", "Serial_RTS": "WB_RTS", "Serial_CTS": "WB_CTS",
    "RESET": "WB_NRST", "CONFIG": "WB_CONFIG_N", "CPU_STATUS_LED": "WB_CPU_STATUS",
    "LED_RX": "WB_LED_RX", "LED_TX": "WB_LED_TX", "ETH0_LINK_LED": "WB_ETH_LINK", "ETH4_LINK_LED": "WB_ETH2_LINK",
    "TX_P0": "RETH_TXP", "TX_N0": "RETH_TXN", "RX_P0": "RETH_RXP", "RX_N0": "RETH_RXN", "ETH_BIAS": "RETH_BIAS",
    "TX_P4": "RETH2_TXP", "TX_N4": "RETH2_TXN", "RX_P4": "RETH2_RXP", "RX_N4": "RETH2_RXN"},
    "operfly_ayak:Microhard_pMDDL_OEM")
g = Izgara(50, 250, sutun=10)
for ag, n in (("+3V3", 2), ("+5V_RF", 2)):
    k.C(rd, g, "22u 16V", ag, fp=C1206)
    for _ in range(n):
        k.C(rd, g, "100n", ag)
k.C(rd, g, "100p", "+5V_RF")
rd.metin("SERI ARAYUZ (3,3 V): uretici RxD ve TxD'nin 0R uzerinden disari alinmasini ister (modul kurtarma islemi icin): 0R + olcum noktalari.", 30, 300)
g = Izgara(50, 335, sutun=10)
k.R(rd, g, "0R", "WB_RXD", "WB_RXD_M"); k.R(rd, g, "0R", "WB_TXD", "WB_TXD_M")
k.R(rd, g, "10k", "+3V3", "WB_NRST"); k.R(rd, g, "10k", "+3V3", "WB_CONFIG_N")
for ag in ("WB_RXD_M", "WB_TXD_M", "WB_CONFIG_N", "WB_NRST"):
    k.olcum_noktasi(rd, g, ag)
rd.metin("ISIKLAR: modul cikislari en cok 8 mA verir ve acilista belirsizdir; 1 k seri direnc, 10 k asagi cekme.", 30, 385)
g = Izgara(50, 420, sutun=12)
for ag, ad in (("WB_CPU_STATUS", "mavi (modul)"), ("WB_LED_RX", "yesil (alis)"), ("WB_LED_TX", "kirmizi (veris)"),
               ("WB_ETH_LINK", "sari (Ethernet 1)"), ("WB_ETH2_LINK", "sari (Ethernet 2)")):
    if ag == "WB_ETH2_LINK":
        g.satir()
    k.R(rd, g, "1k", ag, ag + "_A"); k.iki(rd, g, "Device:LED", "D", "LED " + ad, "GND", ag + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(rd, g, "10k", ag, "GND")

rd.metin("ETHERNET (10/100), iki port: modulun LAN portu 1. omurga portunun, WAN portu 2. omurga portunun A (gonderme) ve B (alma) ciftlerine.", 330, 28)
rd.metin("Devre ureticinin ornegidir (Ek C): her hatta 49,9 ohm, cift ortasi 100 nF ile topraga; trafonun modul tarafi orta uclari ferrit uzerinden", 330, 34)
rd.metin("ETH_BIAS'a. Kablo tarafi orta uclari 75 ohm + 1 nF / 2 kV ile topraga. Ikinci port ayni devreyle cizildi (dogrulanacak: README).", 330, 40)
g = Izgara(350, 90, sutun=12)
for on, a_, b_ in (("RETH", "ETH", "RETH_BS"), ("RETH2", "ETH2", "RETH2_BS")):
    k.parca(rd, g, "Transformer:PT61017PEL", "T", "PT61017PEL (10/100, 1:1)", {
        "TD+": on + "_TXP", "TD-": on + "_TXN", "C_TD": on + "_CT", "RD+": on + "_RXP", "RD-": on + "_RXN", "C_RD": on + "_CT",
        "TX+": a_ + "_A+", "TX-": a_ + "_A-", "C_TX": on + "_CT_A", "RX+": a_ + "_B+", "RX-": a_ + "_B-", "C_RX": on + "_CT_B"},
        "Transformer_SMD:Transformer_Ethernet_Bourns_PT61017PEL", bosluk=2, dx=25)
    k.R(rd, g, "49R9 1%", on + "_TXP", on + "_TERM_TX"); k.R(rd, g, "49R9 1%", on + "_TXN", on + "_TERM_TX"); k.C(rd, g, "100n", on + "_TERM_TX")
    k.R(rd, g, "49R9 1%", on + "_RXP", on + "_TERM_RX"); k.R(rd, g, "49R9 1%", on + "_RXN", on + "_TERM_RX"); k.C(rd, g, "100n", on + "_TERM_RX")
    g.satir()
    k.iki(rd, g, "Device:FerriteBead", "FB", "BLM18HD102SN1D", "RETH_BIAS", on + "_CT", FB0603)
    k.C(rd, g, "100n", on + "_CT")
    k.R(rd, g, "75R", on + "_CT_A", b_); k.R(rd, g, "75R", on + "_CT_B", b_); k.C(rd, g, "1n 2kV", b_, fp=C1206)
    if on == "RETH":
        k.C(rd, g, "100n", "RETH_BIAS")
    g.satir()

rd.metin("3,3 V (AP63203, 12 V'tan, 2 A): modulun sayisal kati 0,5 A'ya kadar ceker; dugum islemcisi de bu raydadir. Radio'daki devrenin aynisi.", 330, 330)
g = Izgara(350, 365, sutun=12)
k.parca(rd, g, "Regulator_Switching:AP63203WU", "U", "AP63203QWU",
        {"IN": "+12V", "EN": "EN_3V3", "GND": "GND", "SW": "SW_3V3", "BST": "BST_3V3", "FB": "+3V3"}, TSOT6)
k.R(rd, g, "100k", "+12V", "EN_3V3"); k.C(rd, g, "10u 50V", "+12V", fp=C1206); k.C(rd, g, "100n", "BST_3V3", "SW_3V3")
k.iki(rd, g, "Device:L", "L", "3u3 XAL4020-332", "SW_3V3", "+3V3", XAL)
k.C(rd, g, "22u 16V", "+3V3", fp=C1206); k.C(rd, g, "22u 16V", "+3V3", fp=C1206); k.bayrak(rd, g, "+3V3")

rd.metin("5 V VERICI BESLEMESI (AP63201, 12 V'tan; Radio'daki devre): verici kati 30 dBm'de ortalama 1,2 A, anlik 1,5 A ceker. Sifirlamada ACIK;", 330, 420)
rd.metin("islemci WB_RF_OFF = 1 ile vericiyi susturabilir. Cikis = 0,8 V x (1 + 158k / 30k1) = 5,0 V.", 330, 426)
g = Izgara(350, 465, sutun=12)
k.parca(rd, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+12V", "EN": "EN_RF", "GND": "GND", "SW": "SW_RF", "BST": "BST_RF", "FB": "FB_RF"}, TSOT6)
k.R(rd, g, "100k", "+12V", "EN_RF"); k.C(rd, g, "10u 50V", "+12V", fp=C1206); k.C(rd, g, "100n", "BST_RF", "SW_RF")
k.iki(rd, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_RF", "+5V_RF", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(rd, g, "22u 16V", "+5V_RF", fp=C1206); k.C(rd, g, "22u 16V", "+5V_RF", fp=C1206); k.bayrak(rd, g, "+5V_RF")
g.satir()
k.R(rd, g, "158k 1%", "+5V_RF", "FB_RF"); k.R(rd, g, "30k1 1%", "FB_RF", "GND"); k.C(rd, g, "100p", "+5V_RF", "FB_RF")
x, y = g.yer()
k.koy(rd, N7002[0], N7002[1], N7002[2], x, y, {"D": "EN_RF", "S": "GND", "G": "WB_RF_OFF"}, SOT23)
k.R(rd, g, "100k", "WB_RF_OFF", "GND")
k.R(rd, g, "10k 1%", "+5V_RF", "WB_VRF_SENS"); k.R(rd, g, "10k 1%", "WB_VRF_SENS", "GND"); k.C(rd, g, "100n", "WB_VRF_SENS")
rd.yaz(os.path.join(BURASI, "genisbant.kicad_sch"))

# --- Kumanda radyosu (RX kartındaki devre) --------------------------------------------------
km = Sema(k.P, "Ground Radio - kumanda radyosu", kagit="A2", tarih=k.T, ust=kok, ad="Kumanda", genel_etiket=True)
kok.alt_sayfa(km, "kumanda.kicad_sch", 177.8, 50.8)
km.metin("KUMANDA RADYO MODULU (RFDesign RFD900ux-SMT; 868 MHz icin RFD868ux-SMT ayni yere oturur): RX kartindaki baglantinin aynisi.", 30, 28)
km.metin("Seri arayuz 3,3 V (en cok 3,5 V). USB uclari uretici tarafindan devre disi, bos. +3V3_OUT modulun kendi regulator cikisi, yuklenmez.", 30, 34)
km.metin("Islemciden module giden hatlarda 470R: modul beslemesi kapaliyken girislerinden akim akmasini sinirlar. GPIO uclari kullanilmaz.", 30, 40)
k.koy(km, "operfly:RFD900ux-SMT", "U", "RFD900ux-SMT (secenek: RFD868ux-SMT)", 100, 95, {
    "+5V": "+5V3_KUM", "GND": "GND", "RX": "KUM_RX_M", "TX": "KUM_TXD", "RTS": "KUM_RTS", "CTS": "KUM_CTS_M",
    "SWO": "KUM_SWO", "ANT1": "KUM_ANT1", "ANT2": "KUM_ANT2", "+3V3_OUT": "KUM_3V3"}, "operfly_ayak:RFDesign_RFD900ux-SMT")
g = Izgara(50, 160, sutun=9)
for a, b in (("KUM_RXD", "KUM_RX_M"), ("KUM_CTS", "KUM_CTS_M"), ("KUM_BOOT_N", "KUM_SWO")):
    k.R(km, g, "470R", a, b)
k.C(km, g, "22u 16V", "+5V3_KUM", fp=C1206); k.C(km, g, "100n", "+5V3_KUM"); k.C(km, g, "100p", "+5V3_KUM")
g.satir()
for ag in ("KUM_TXD", "KUM_RX_M", "KUM_SWO", "KUM_3V3"):
    k.olcum_noktasi(km, g, ag)
km.metin("ANTENLER: iki giris, modul iyi olani kendisi secer (cesitleme). Hatlar 50 ohm, dogrudan konnektore (uretici onerisi).", 30, 225)
g = Izgara(50, 260, sutun=9)
SMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
for i in (1, 2):
    x, y = g.yer(); g.yer()
    k.koy(km, "Connector:Conn_Coaxial", "J", "KUMANDA ANT %d (SMA)" % i, x + 5, y, {"In": "KUM_ANT%d" % i, "Ext": "GND"}, SMA)
km.metin("MODUL BESLEMESI (AP63201, 12 V -> 5,3 V; RX kartindaki devre): modul 5,0-5,5 V ister ve verirken 1 A tepe akim ceker.", 270, 28)
km.metin("Besleme sifirlamada ACIKTIR; islemci KUM_OFF = 1 ile keser (modulde sifirlama ucu yok). Cikis = 0,8 V x (1 + 169k / 30k1) = 5,29 V.", 270, 34)
g = Izgara(290, 86, sutun=9)
k.parca(km, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+12V", "EN": "KUM_EN", "GND": "GND", "SW": "SW_KUM", "BST": "BST_KUM", "FB": "FB_KUM"}, TSOT6)
k.R(km, g, "100k", "+12V", "KUM_EN"); k.C(km, g, "10u 50V", "+12V", fp=C1206); k.C(km, g, "100n", "BST_KUM", "SW_KUM")
k.iki(km, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_KUM", "+5V3_KUM", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(km, g, "22u 16V", "+5V3_KUM", fp=C1206); k.C(km, g, "22u 16V", "+5V3_KUM", fp=C1206)
g.satir()
k.R(km, g, "169k 1%", "+5V3_KUM", "FB_KUM"); k.R(km, g, "30k1 1%", "FB_KUM", "GND"); k.C(km, g, "100p", "+5V3_KUM", "FB_KUM")
k.bayrak(km, g, "+5V3_KUM")
x, y = g.yer()
k.koy(km, N7002[0], N7002[1], N7002[2], x, y, {"D": "KUM_EN", "S": "GND", "G": "KUM_OFF"}, SOT23)
k.R(km, g, "100k", "KUM_OFF", "GND")
km.metin("BESLEME OLCUMU: islemci modul gerilimini okur (10 k / 10 k, 5,3 V -> 2,65 V).", 270, 170)
g = Izgara(290, 205, sutun=9)
k.R(km, g, "10k 1%", "+5V3_KUM", "KUM_VSENS"); k.R(km, g, "10k 1%", "KUM_VSENS", "GND"); k.C(km, g, "100n", "KUM_VSENS")
km.yaz(os.path.join(BURASI, "kumanda.kicad_sch"))

# --- Güç girişi ve ek omurga portları -------------------------------------------------------
gp = Sema(k.P, "Ground Radio - dis besleme, omurga portlari", kagit="A2", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gp, "guc.kicad_sch", 254.0, 50.8)
gp.metin("DIS BESLEME GIRISI (XT30, 9-16 V: 3-4 hucreli batarya ya da 12 V adaptor). Sigorta 7 A; ters baglantida ve geri beslemede diyot keser,", 30, 28)
gp.metin("18 V ustunu kirpma diyodu keser (surerse sigorta atar). +12V_BARA yer tarafinin ortak 12 V barasidir: kart ve dort port buradan beslenir.", 30, 34)
gp.metin("VEXT_SENS = giris gerilimi / 11 (islemci olcer). Kartin kendi +12V'u baradan ayri bir diyotla alinir (portlardan da beslenebilir).", 30, 40)
g = Izgara(50, 80, sutun=12)
x, y = g.yer(); g.yer()
k.koy(gp, "Connector_Generic:Conn_01x02", "J", "Dis besleme (XT30)", x + 5, y, {"Pin_1": "VEXT_IN", "Pin_2": "GND"}, "Connector_AMASS:AMASS_XT30U-M_1x02_P5.0mm_Vertical")
k.iki(gp, g, "Device:Fuse", "F", "7 A (Nano2 0451007)", "VEXT_IN", "VEXT_F", "Fuse:Fuse_Littelfuse-NANO2-451_453")
k.iki(gp, g, "Device:D_Schottky", "D", "PDS760 (60 V, 7 A)", "+12V_BARA", "VEXT_F", "Diode_SMD:D_PowerDI-5")
k.iki(gp, g, "Device:D_TVS", "D", "SMBJ18A", "+12V_BARA", "GND", "Diode_SMD:D_SMB")
k.C(gp, g, "10u 50V", "+12V_BARA", fp=C1206); k.C(gp, g, "10u 50V", "+12V_BARA", fp=C1206); k.C(gp, g, "100n 50V", "+12V_BARA", fp=C0603)
k.R(gp, g, "100k 1%", "VEXT_F", "VEXT_SENS"); k.R(gp, g, "10k 1%", "VEXT_SENS", "GND"); k.C(gp, g, "100n", "VEXT_SENS")
g.satir()
k.iki(gp, g, "Device:D_Schottky", "D", "B360A (60 V, 3 A)", "+12V", "+12V_BARA", "Diode_SMD:D_SMA")
k.olcum_noktasi(gp, g, "+12V_BARA")

gp.metin("OMURGA PORTLARI: 1. port Dugum sayfasindadir. Dort portun CAN hatlari ortaktir (yildizin merkezi bu kart; sonlandirma 60 ohm).", 30, 150)
gp.metin("Her portun 12 V'u ayri, kendini onaran 2 A sigortadan gecer. Ethernet: 1. port = modulun LAN portu, 2. port = WAN portu (koprulenir);", 30, 156)
gp.metin("3. ve 4. portlarda Ethernet yoktur (Base ve Tracker icin: CAN + 12 V).", 30, 162)
g = Izgara(50, 200, sutun=12)
k.iki(gp, g, "Device:Polyfuse", "F", "2 A tutma (1812)", "+12V_BARA", "+12V_BUS", "Fuse:Fuse_1812_4532Metric")
for n in (2, 3, 4):
    k.iki(gp, g, "Device:Polyfuse", "F", "2 A tutma (1812)", "+12V_BARA", "+12V_P%d" % n, "Fuse:Fuse_1812_4532Metric")
    k.bayrak(gp, g, "+12V_P%d" % n)
for n, x in ((2, 80), (3, 200), (4, 320)):
    b = {"+12V": "+12V_P%d" % n, "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L"}
    if n == 2:
        b.update({"ETH_A+": "ETH2_A+", "ETH_A-": "ETH2_A-", "ETH_B+": "ETH2_B+", "ETH_B-": "ETH2_B-"})
    k.koy(gp, "operfly:Operfly_Bus_20", "J", "Operfly Bus (port %d)" % n, x, 300, b, GECKO)
gp.yaz(os.path.join(BURASI, "guc.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_groundradio.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, rd, km, gp], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_groundradio (kok + 4 sayfa)")
