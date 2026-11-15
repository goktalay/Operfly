"""Operfly Vision şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py VISION operfly_vision`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + NVIDIA Jetson Orin NX / Orin Nano soketi + iki kamera portu (her biri ayrı PCIe gigabit denetleyici)
+ omurga Ethernet'i (Jetson'ın kendi portu) + M.2 NVMe + IMU + beslemeler.
Kaynak belgeler: Jetson Orin NX Data Sheet (DS-10712-001), Intel I210 Datasheet (333016, v3.7), TPS2663 ve TPS62130 veri sayfaları.
Jetson çevresindeki bağlantılar (PCIe kondansatörleri, M.2, USB algılama) açık kaynak bir Jetson Orin taşıyıcı kartıyla da karşılaştırıldı.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_vision", "2026-11-15")
kok = Sema(k.P, "Operfly Vision", kagit="A3", tarih=k.T)
kok.metin("Operfly Vision - goruntu isleme karti, Jetson tasiyici (OPFVIS)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/VISION/kicad/uret.py.", 25.4, 33.02, 1.6)

EK = {"PA0": "JET_IMON", "PA1": "CAM1_IMON", "PA2": "CAM2_IMON",       # ADC1_IN0-2: sigorta akim cikislari
      "PA4": "JET_VIN_EN",                         # 1: Jetson'a 12 V ver (sifirlamada kapali)
      "PA5": "JET_POWER_EN",                       # 1: modul acilir (VDD_IN kararli olduktan sonra)
      "PA6": "JET_SHDN_REQ_N",                     # 0: modul kapanmak istiyor -> POWER_EN indirilir
      "PA7": "JET_RESET",                          # 1: SYS_RESET* dusuge cekilir
      "PB0": "JET_RECOVERY",                       # 1: FORCE_RECOVERY* dusuk (acilirken tutulursa USB kurtarma kipi)
      "PB1": "JET_MODULE_ID",                      # 1: 5-20 V destekli modul; 0: yalniz 5 V'luk eski modul -> 12 V VERILMEZ
      "PB3": "JET_RUN",                            # 1: tasiyici 3,3 V'u acik (modul SYS_RESET*'i birakti)
      "PB4": "CAM1_EN", "PB6": "CAM2_EN",          # 1: kamera portuna 12 V ver
      "PB7": "FAN_TACH",                           # fan devir darbesi
      "PB10": "MCU_TX", "PB11": "MCU_RX",          # USART3: Jetson UART1 (seviye ceviriciden)
      "PA8": "PWR_FLT_N"}                          # 0: sigortalardan biri hata verdi
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, ethernet=True, pps=True, besleme="kart")
N7002 = ("Transistor_FET:2N7002", "Q", "2N7002", "Package_TO_SOT_SMD:SOT-23")
BUS_FP = "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical"
TRAFO = "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13"


def sigorta(sema, x, y, g, p, cikis, rilim, rimon, en):
    """TPS26630: giris +12V, cikis `cikis`. en: islemci ucu agi (1 = acik)."""
    k.koy(sema, "Power_Management:TPS26630RGE", "U", "TPS26630RGER", x, y, {
        "IN": "+12V", "IN_SYS": "+12V", "UVLO": "VIS_UVLO", "OVP": "VIS_OVP", "GND": "GND", "MODE": "GND", "dVdT": p + "_DVDT", "ILIM": p + "_ILIM",
        "~{SHDN}": en, "IMON": p + "_IMON", "~{FLT}": "PWR_FLT_N", "PGTH": p + "_PGTH", "OUT": cikis},
        "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias")
    k.C(sema, g, "100n 50V", "+12V", fp=C0603); k.C(sema, g, "1u 25V", cikis, fp=C0603)
    k.R(sema, g, rilim, p + "_ILIM", "GND"); k.C(sema, g, "47n", p + "_DVDT")
    k.R(sema, g, rimon, p + "_IMON", "GND"); k.C(sema, g, "100n", p + "_IMON")
    k.R(sema, g, "47k", en, "GND")
    k.R(sema, g, "100k 1%", cikis, p + "_PGTH"); k.R(sema, g, "13k7 1%", p + "_PGTH", "GND")


def regulator(sema, g, ag, rust, en, pg=None):
    n = "REG" + ag.replace("+", "_")
    aglar = {"VIN": "+12V", "EN": en, "GND": "GND", "SW": n + "_SW", "VOS": ag, "FB": n + "_FB", "SS/TR": n + "_SS", "DEF": "GND", "FSW": "GND"}
    if pg:
        aglar["PG"] = pg
    k.parca(sema, g, "Regulator_Switching:TPS62130", "U", "TPS62130RGTR", aglar, "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias", bosluk=2, dx=20)
    k.C(sema, g, "10u 25V", "+12V", fp=C1206); k.C(sema, g, "100n 25V", "+12V", fp=C0603)
    k.iki(sema, g, "Device:L", "L", "2u2 XAL4020-222", n + "_SW", ag, "Inductor_SMD:L_Coilcraft_XAL4020-XXX")
    k.C(sema, g, "22u 10V", ag, fp=C1206); k.C(sema, g, "22u 10V", ag, fp=C1206)
    k.R(sema, g, rust, ag, n + "_FB"); k.R(sema, g, "100k 1%", n + "_FB", "GND"); k.C(sema, g, "3n3", n + "_SS")
    k.olcum_noktasi(sema, g, ag); k.bayrak(sema, g, ag)


def trafo(sema, x, y, g, p, cip, kablo):
    """cip / kablo: cift harfi -> (arti agi, eksi agi). Orta uclar: cip tarafi 100n -> GND, kablo tarafi 75R -> 1n 2kV."""
    tr = {}
    for c, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
        tr.update({str(cp): cip[c][0], str(cm): cip[c][1], str(cc): "%s_CT_%s" % (p, c), str(kp_): kablo[c][0], str(km_): kablo[c][1], str(kc_): "%s_KCT_%s" % (p, c)})
    k.koy(sema, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", x, y, tr, TRAFO)
    for c in "ABCD":
        k.C(sema, g, "100n", "%s_CT_%s" % (p, c))
    for c in "ABCD":
        k.R(sema, g, "75R", "%s_KCT_%s" % (p, c), p + "_BS")
    k.C(sema, g, "1n 2kV", p + "_BS", fp=C1206)


# --- Güç ---------------------------------------------------------------------------
gc = Sema(k.P, "Operfly Vision - giris korumasi, sigortalar, 3,3 V ve 1,8 V", kagit="A1", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gc, "guc.kicad_sch", 101.6, 50.8)
gc.metin("GIRIS: omurga 12 V'u ters baglanti korumasindan (P kanal MOSFET) gecer. Bu kart 3-4 A cektigi icin dugumun 3 A'lik diyodu kullanilmaz.", 30, 28)
gc.metin("UVLO / OVP boluculeri uc sigortada ortak: 9,6 V altinda ve 15,3 V ustunde cikislar kapanir.", 30, 34)
g = Izgara(50, 75, sutun=12)
x, y = g.yer()
k.koy(gc, "Transistor_FET:SUD50P04-08", "Q", "SUD50P04-08", x, y, {"D": "+12V_BUS", "S": "+12V", "G": "REV_GATE"}, "Package_TO_SOT_SMD:TO-252-2")
k.R(gc, g, "10k", "REV_GATE", "GND"); k.iki(gc, g, "Diode:BZT52Bxx", "D", "BZT52B10 (10 V)", "+12V", "REV_GATE", "Diode_SMD:D_SOD-123F")
k.C(gc, g, "100u 25V", "+12V", fp="Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D")
k.R(gc, g, "100k 1%", "+12V", "VIS_UVLO"); k.R(gc, g, "14k3 1%", "VIS_UVLO", "GND")
k.R(gc, g, "100k 1%", "+12V", "VIS_OVP"); k.R(gc, g, "8k66 1%", "VIS_OVP", "GND")
k.R(gc, g, "10k", "+3V3", "PWR_FLT_N")

gc.metin("JETSON BESLEMESI (TPS26630, akim siniri 18 / 4k53 = 4 A): modul 5-20 V kabul eder, 12 V dogrudan verilir. Islemci once MODULE_ID'yi okur;", 30, 120)
gc.metin("eski (yalniz 5 V) modul takiliysa JET_VIN_EN verilmez. IMON = akim x 27,9 uA/A x 27k (4 A -> 3,0 V).", 30, 126)
g = Izgara(120, 165, sutun=10)
sigorta(gc, 70, 175, g, "JET", "+12V_JET", "4k53 1%", "27k 1%", "JET_VIN_EN")
k.C(gc, g, "100u 25V", "+12V_JET", fp="Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D"); k.C(gc, g, "100u 25V", "+12V_JET", fp="Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D")

gc.metin("KAMERA PORTU BESLEMELERI (TPS26630, akim siniri 18 / 12k = 1,5 A): port basina 12 V, islemci acar. IMON 68k (1,5 A -> 2,8 V).", 30, 230)
for i in (1, 2):
    g = Izgara(120, 275 + (i - 1) * 110, sutun=10)
    sigorta(gc, 70, 285 + (i - 1) * 110, g, "CAM%d" % i, "CAM%d_12V" % i, "12k 1%", "68k 1%", "CAM%d_EN" % i)

gc.metin("TASIYICI BESLEMELERI: modul SYS_RESET*'i biraktiginda (1,8 V) acilir; ondan once kart Jetson uclarina gerilim vermez (uretici kurali).", 420, 28)
gc.metin("+3V3_JET: Ethernet denetleyicileri, 1,8 V regulatoru. +3V3_M2: yalnizca NVMe. Cikis = 0,8 V x (1 + 316k / 100k) = 3,33 V, 3 A.", 420, 34)
g = Izgara(440, 80, sutun=14)
regulator(gc, g, "+3V3_JET", "316k 1%", "JET_SYS_RESET_N", pg="JET_RUN")
k.R(gc, g, "10k", "+3V3", "JET_RUN")
g = Izgara(440, 170, sutun=14)
regulator(gc, g, "+3V3_M2", "316k 1%", "JET_SYS_RESET_N")
gc.metin("+1V8_JET (LP5907-1.8): IMU ve seviye ceviricinin Jetson tarafi. Jetson'in giris-cikislari 1,8 V'tur.", 420, 250)
g = Izgara(440, 290, sutun=14)
k.parca(gc, g, "Regulator_Linear:LP5907MFX-1.8", "U", "LP5907MFX-1.8", {"IN": "+3V3_JET", "EN": "+3V3_JET", "GND": "GND", "OUT": "+1V8_JET"}, "Package_TO_SOT_SMD:SOT-23-5", bosluk=1, dx=14)
k.C(gc, g, "1u", "+3V3_JET"); k.C(gc, g, "1u", "+1V8_JET"); k.olcum_noktasi(gc, g, "+1V8_JET")
gc.yaz(os.path.join(BURASI, "guc.kicad_sch"))

# --- Jetson ----------------------------------------------------------------------
jt = Sema(k.P, "Operfly Vision - Jetson Orin NX / Orin Nano soketi ve denetim devreleri", kagit="A1", tarih=k.T, ust=kok, ad="Jetson", genel_etiket=True)
kok.alt_sayfa(jt, "jetson.kicad_sch", 177.8, 50.8)
jt.birim_araligi = 200
jt.metin("JETSON SOKETI (260 uclu SO-DIMM). Birimler: guc ve denetim | PCIe, Ethernet, USB | dusuk hizli giris-cikislar | kullanilmayan goruntu uclari.", 30, 25)
jt.metin("Uc tablosu uretici veri sayfasindan (10_ORTAK_ARACLAR/kicad/jetson_uclari.py). Bos birakilan uclar bu kartta kullanilmaz.", 30, 31)
J = {"VDD_IN": "+12V_JET", "GND": "GND", "POWER_EN": "JET_POWER_EN_R", "SYS_RESET*": "JET_SYS_RESET_N", "SHUTDOWN_REQ*": "JET_SHDN_REQ_12V",
     "FORCE_RECOVERY*": "JET_FRC_N", "MODULE_ID": "JET_MODULE_ID", "MOD_SLEEP*": "JET_MOD_SLEEP_N", "SLEEP/WAKE*": "JET_SLEEP_WAKE_N",
     "PCIE0_CLK_P": "M2_CLK_P", "PCIE0_CLK_N": "M2_CLK_N", "PCIE0_RST*": "M2_RST_N", "PCIE0_CLKREQ*": "M2_CLKREQ_N", "PCIE_WAKE*": "PCIE_WAKE_N",
     "USB0_D_P": "USB0_DP", "USB0_D_N": "USB0_DM", "GPIO00": "USB0_VBUS_DET_N",
     "UART1_TXD": "JET_UART_TX_1V8", "UART1_RXD": "JET_UART_RX_1V8", "UART2_TXD": "JET_DBG_TX", "UART2_RXD": "JET_DBG_RX",
     "SPI0_SCK": "IMU_SCK", "SPI0_MOSI": "IMU_MOSI", "SPI0_MISO": "IMU_MISO", "SPI0_CS0*": "IMU_CS_N", "GPIO09": "IMU_INT",
     "GPIO07": "JET_PPS_1V8", "GPIO14": "JET_FAN_PWM_1V8"}
for l in range(4):
    for s_ in "PN":
        J["PCIE0_RX%d_%s" % (l, s_)] = "M2_PER%d_%s" % (l, s_)
        J["PCIE0_TX%d_%s" % (l, s_)] = "J_PCIE0_TX%d_%s" % (l, s_)
        J["GBE_MDI%d_%s" % (l, s_)] = "JGBE_MDI%d_%s" % (l, s_)
for n in (1, 2):
    e = "E%d" % n
    J.update({"PCIE%d_RX0_P" % n: e + "_PET_C_P", "PCIE%d_RX0_N" % n: e + "_PET_C_N", "PCIE%d_TX0_P" % n: "J_PCIE%d_TX_P" % n, "PCIE%d_TX0_N" % n: "J_PCIE%d_TX_N" % n,
              "PCIE%d_CLK_P" % n: e + "_CLK_P", "PCIE%d_CLK_N" % n: e + "_CLK_N", "PCIE%d_RST*" % n: e + "_RST_N", "PCIE%d_CLKREQ*" % n: e + "_CLKREQ_N"})
k.koy(jt, "operfly:Jetson_Orin_NX", "J", "Jetson Orin NX / Orin Nano", 110, 150, J, "Connector_PCBEdge:SODIMM-260_DDR4_H4.0-5.2_OrientationStd_Socket")

jt.metin("DENETIM: POWER_EN islemciden (1k seri; modulde 100k asagi cekme). SHUTDOWN_REQ* modulde 5k ile 12 V'a cekilidir -> 100k/33k ile islemciye.", 30, 290)
jt.metin("SYS_RESET* ve FORCE_RECOVERY* 1,8 V hatlardir: islemci yalnizca transistorle DUSUGE ceker, hicbir zaman yuksege surmez.", 30, 296)
jt.metin("MODULE_ID: Orin'de bosta (100k ile 3,3 V'a cekilir = 1), yalniz 5 V'luk eski modulde GND.", 30, 302)
g = Izgara(50, 340, sutun=14)
k.R(jt, g, "1k", "JET_POWER_EN", "JET_POWER_EN_R"); k.R(jt, g, "100k", "JET_POWER_EN", "GND")
k.R(jt, g, "100k 1%", "JET_SHDN_REQ_12V", "JET_SHDN_REQ_N"); k.R(jt, g, "33k 1%", "JET_SHDN_REQ_N", "GND"); k.C(jt, g, "1n", "JET_SHDN_REQ_N")
k.R(jt, g, "100k", "+3V3", "JET_MODULE_ID")
for ag, kapi in (("JET_SYS_RESET_N", "JET_RESET"), ("JET_FRC_N", "JET_RECOVERY")):
    x, y = g.yer()
    k.koy(jt, N7002[0], N7002[1], N7002[2], x, y, {"D": ag, "S": "GND", "G": kapi}, N7002[3])
    k.R(jt, g, "100k", kapi, "GND")
for ag in ("JET_SYS_RESET_N", "JET_FRC_N", "JET_MOD_SLEEP_N", "JET_SLEEP_WAKE_N", "JET_DBG_TX", "JET_DBG_RX"):
    k.olcum_noktasi(jt, g, ag)
jt.metin("PCIe: Jetson'in verici ciftlerinde 220 nF (alicilarin kondansatoru karsi taraftadir). Ethernet denetleyicilerinde saat istegi ucu yok:", 30, 400)
jt.metin("PCIE1/PCIE2 CLKREQ* 0R ile GND'ye (saat surekli). Kondansatorler Jetson soketinin yanina konur.", 30, 406)
g = Izgara(50, 440, sutun=20, dx=20)
for l in range(4):
    for s_ in "PN":
        k.C(jt, g, "220n", "J_PCIE0_TX%d_%s" % (l, s_), "M2_PET%d_%s" % (l, s_))
for n in (1, 2):
    for s_ in "PN":
        k.C(jt, g, "220n", "J_PCIE%d_TX_%s" % (n, s_), "E%d_PER_%s" % (n, s_))
    k.R(jt, g, "0R", "E%d_CLKREQ_N" % n, "GND")
jt.yaz(os.path.join(BURASI, "jetson.kicad_sch"))

# --- Ethernet ---------------------------------------------------------------------
et = Sema(k.P, "Operfly Vision - omurga Ethernet'i ve iki kamera portu (I210)", kagit="A0", tarih=k.T, ust=kok, ad="Ethernet", genel_etiket=True)
kok.alt_sayfa(et, "ethernet.kicad_sch", 254.0, 50.8)
et.metin("OMURGA ETHERNET'I: Jetson'in kendi gigabit portu (PHY modulun icinde) trafo uzerinden omurga fisinin dort ciftine gider.", 30, 25)
g = Izgara(150, 55, sutun=9, dx=24)
trafo(et, 80, 70, g, "BB", {c: ("JGBE_MDI%d_P" % i, "JGBE_MDI%d_N" % i) for i, c in enumerate("ABCD")}, {c: ("ETH_%s+" % c, "ETH_%s-" % c) for c in "ABCD"})
et.metin("KAMERA PORTLARI: her port ayri bir PCIe gigabit denetleyici (Intel I210-IT). Kamera akisi omurgayla ve diger kamerayla hat paylasmaz;", 30, 125)
et.metin("her portta donanim zaman damgasi (PTP) vardir. Konnektor Operfly Bus'tir: 12 V (sigortali), Ethernet ve PPS (tetikleme). CAN baglanmaz.", 30, 131)
et.metin("I210: besleme tam tumlesik (1,5 V ve 0,9 V'u kendi uretir, CTOP-CBOT 39 nF), RSET 4k99, 25 MHz kristal + 27 pF, ayar icin SPI flash.", 30, 137)
et.metin("Kullanilmayan NC-SI, SMBus ve JTAG uclari uretici tablosundaki gibi cekilir. SDP1 <- omurga PPS'i, SDP0 -> kamera tetiklemesi.", 30, 143)
for n in (1, 2):
    e, y0 = "E%d" % n, 250 + (n - 1) * 300
    et.metin("KAMERA PORTU %d (PCIE%d)" % (n, n), 30, y0 - 85, 2.5)
    V, GD = "+3V3_JET", "GND"
    ust = {4: "TDO", 5: "NRX1", 6: "NRX0", 8: "NTX1", 9: "NTX0", 16: "WAKE", 18: "TMS", 28: "DEVOFF", 29: "TDI", 34: "SMBC", 35: "SMBA", 36: "SMBD", 1: "PG"}
    alt = {2: "NCLK", 3: "NCRS", 7: "NTXEN", 19: "TCK", 12: "NVM_SI"}
    a = {10: V, 27: V, 41: V, 51: V, 64: V, 65: GD, 11: e + "_0V9", 32: e + "_0V9", 42: e + "_0V9", 59: e + "_0V9", 38: e + "_0V9",
         47: e + "_1V5", 56: e + "_1V5", 39: e + "_1V5", 37: e + "_CBOT", 40: e + "_CTOP", 48: e + "_RSET", 45: e + "_XO", 46: e + "_XI",
         13: e + "_NVM_SK", 14: e + "_NVM_SO", 15: e + "_NVM_CS", 17: e + "_RST_N", 20: e + "_PET_N", 21: e + "_PET_P", 23: e + "_PER_N", 24: e + "_PER_P",
         25: e + "_CLK_N", 26: e + "_CLK_P", 31: e + "_LED", 61: e + "_SDP1", 63: e + "_SDP0",
         58: e + "_MDI0_P", 57: e + "_MDI0_N", 55: e + "_MDI1_P", 54: e + "_MDI1_N", 53: e + "_MDI2_P", 52: e + "_MDI2_N", 50: e + "_MDI3_P", 49: e + "_MDI3_N"}
    a.update({no: "%s_%s" % (e, ad) for no, ad in list(ust.items()) + list(alt.items())})
    k.koy(et, "Interface_Ethernet:WGI210AT", "U", "WGI210IT", 110, y0, {str(no): ag for no, ag in a.items()}, "Package_DFN_QFN:QFN-64-1EP_9x9mm_P0.5mm_EP4.7x4.7mm")
    g = Izgara(40, y0 + 75, sutun=22, dx=20)
    for ad in ust.values():
        k.R(et, g, "10k", V, "%s_%s" % (e, ad))
    for ad in alt.values():
        k.R(et, g, "10k", "%s_%s" % (e, ad), GD)
    g.satir()
    for _ in range(5):
        k.C(et, g, "100n", V)
    k.C(et, g, "22u 10V", V, fp=C1206)
    for _ in range(4):
        k.C(et, g, "100n", e + "_0V9")
    k.C(et, g, "22u 6V3", e + "_0V9", fp=C0805)
    for _ in range(2):
        k.C(et, g, "100n", e + "_1V5")
    k.C(et, g, "22u 6V3", e + "_1V5", fp=C0805)
    k.C(et, g, "39n", e + "_CTOP", e + "_CBOT"); k.R(et, g, "4k99 1%", e + "_RSET", GD)
    g.satir()
    k.koy(et, "Device:Crystal_GND24", "Y", "25 MHz 30 ppm", *g.yer(), {"1": e + "_XI", "3": e + "_XO", "2": GD, "4": GD}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
    k.C(et, g, "27p", e + "_XI"); k.C(et, g, "27p", e + "_XO")
    k.C(et, g, "220n", e + "_PET_P", e + "_PET_C_P"); k.C(et, g, "220n", e + "_PET_N", e + "_PET_C_N")
    k.parca(et, g, "Memory_Flash:W25Q32JVSS", "U", "W25Q16JVSSIQ", {"~{CS}": e + "_NVM_CS", "CLK": e + "_NVM_SK", "DI/IO_{0}": e + "_NVM_SI", "DO/IO_{1}": e + "_NVM_SO",
            "~{WP}/IO_{2}": e + "_NVM_WP", "~{HOLD}/~{RESET}/IO_{3}": e + "_NVM_HOLD", "VCC": V, "GND": GD}, "Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", bosluk=2, dx=18)
    k.R(et, g, "10k", V, e + "_NVM_WP"); k.R(et, g, "10k", V, e + "_NVM_HOLD"); k.C(et, g, "100n", V)
    k.iki(et, g, "Device:LED", "D", "LED yesil (baglanti)", e + "_LED", e + "_LED_A", "LED_SMD:LED_0603_1608Metric"); k.R(et, g, "1k", V, e + "_LED_A")
    k.R(et, g, "1k", "PPS_IN", e + "_SDP1"); k.R(et, g, "100R", e + "_SDP0", "CAM%d_PPS" % n)
    gt = Izgara(330, y0 - 15, sutun=9, dx=24)
    trafo(et, 260, y0, gt, e, {c: ("%s_MDI%d_P" % (e, i), "%s_MDI%d_N" % (e, i)) for i, c in enumerate("ABCD")},
          {c: ("CAM%d_ETH_%s+" % (n, c), "CAM%d_ETH_%s-" % (n, c)) for c in "ABCD"})
    port = {"ETH_%s%s" % (c, i): "CAM%d_ETH_%s%s" % (n, c, i) for c in "ABCD" for i in "+-"}
    port.update({"+12V": "CAM%d_12V" % n, "GND": GD, "PPS": "CAM%d_PPS" % n})
    k.koy(et, "operfly:Operfly_Bus_20", "J", "Kamera portu %d" % n, 600, y0, port, BUS_FP)
et.yaz(os.path.join(BURASI, "ethernet.kicad_sch"))

# --- Çevre: M.2, IMU, seviye çevirici, fan, USB -----------------------------------
cv = Sema(k.P, "Operfly Vision - NVMe, IMU, seviye cevirici, fan, kurtarma USB'si", kagit="A1", tarih=k.T, ust=kok, ad="Cevre", genel_etiket=True)
kok.alt_sayfa(cv, "cevre.kicad_sch", 330.2, 50.8)
cv.metin("M.2 NVMe (Key M, PCIE0, dort serit): 3,3 V ayri regulatorden. Soketin PER uclari Jetson'in alici ciftlerine dogrudan,", 30, 28)
cv.metin("PET uclari Jetson'in verici ciftlerine 220 nF uzerinden (Jetson sayfasinda) baglanir.", 30, 34)
M = {"3.3V": "+3V3_M2", "GND": "GND", "~{PERST}": "M2_RST_N", "~{CLKREQ}": "M2_CLKREQ_N", "~{PEWAKE}": "PCIE_WAKE_N", "REFCLKp": "M2_CLK_P", "REFCLKn": "M2_CLK_N",
     "DEVSLP": "M2_DEVSLP", "PERp0/SATA-B-": "M2_PER0_P", "PERn0/SATA-B+": "M2_PER0_N", "PETp0/SATA-A+": "M2_PET0_P", "PETn0/SATA-A-": "M2_PET0_N"}
for l in (1, 2, 3):
    M.update({"PERp%d" % l: "M2_PER%d_P" % l, "PERn%d" % l: "M2_PER%d_N" % l, "PETp%d" % l: "M2_PET%d_P" % l, "PETn%d" % l: "M2_PET%d_N" % l})
k.koy(cv, "Connector:Bus_M.2_Socket_M", "J", "M.2 Key M (NVMe 2242/2280)", 90, 120, M, "Connector_PCBEdge:TE_M.2_M_2x38-1MP_P0.5mm")
g = Izgara(170, 70, sutun=8)
k.R(cv, g, "10k", "M2_DEVSLP", "GND"); k.C(cv, g, "22u 10V", "+3V3_M2", fp=C1206); k.C(cv, g, "22u 10V", "+3V3_M2", fp=C1206)
for _ in range(3):
    k.C(cv, g, "100n", "+3V3_M2")

cv.metin("IMU (ICM-42688-P, Jetson SPI0, 1,8 V): goruntu ile atalet olcumunu ayni saatle eslemek icin karta ozel IMU. INT1 -> GPIO09.", 380, 28)
g = Izgara(400, 70, sutun=10)
k.parca(cv, g, "operfly:ICM-42688-P", "U", "ICM-42688-P", {"AP_CS": "IMU_CS_N", "AP_SCLK": "IMU_SCK", "AP_SDI": "IMU_MOSI", "AP_SDO": "IMU_MISO", "INT1": "IMU_INT",
        "VDD": "+1V8_JET", "VDDIO": "+1V8_JET", "GND": "GND", "RESV7": "GND", "RESV11": "GND"},
        "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm", bosluk=2, dx=20)
k.C(cv, g, "100n", "+1V8_JET"); k.C(cv, g, "100n", "+1V8_JET"); k.C(cv, g, "2u2", "+1V8_JET", fp=C0603)

cv.metin("SEVIYE CEVIRICI (TXS0104E, 1,8 V <-> 3,3 V): Jetson UART1 <-> dugum islemcisi, omurga PPS'i -> GPIO07, fan PWM (GPIO14).", 380, 130)
cv.metin("Jetson kapaliyken (1,8 V yok) cevirici uclarini birakir; kart Jetson'a gerilim vermez.", 380, 136)
g = Izgara(400, 175, sutun=10)
k.parca(cv, g, "Logic_LevelTranslator:TXS0104EPW", "U", "TXS0104EPW", {"V_{CCA}": "+1V8_JET", "V_{CCB}": "+3V3", "OE": "+1V8_JET", "GND": "GND",
        "A1": "JET_UART_TX_1V8", "B1": "MCU_RX", "A2": "JET_UART_RX_1V8", "B2": "MCU_TX", "A3": "JET_PPS_1V8", "B3": "PPS_IN", "A4": "JET_FAN_PWM_1V8", "B4": "FAN_PWM_3V3"},
        "Package_SO:TSSOP-14_4.4x5mm_P0.65mm", bosluk=2, dx=20)
k.C(cv, g, "100n", "+1V8_JET"); k.C(cv, g, "100n", "+3V3")

cv.metin("FAN (5 V, 4 uclu: GND, +5V, devir, PWM): PWM Jetson'dan; Jetson kapaliyken 10k asagi cekme fani durdurur. Devir darbesi islemciye.", 380, 230)
g = Izgara(400, 270, sutun=10)
k.parca(cv, g, "Connector_Generic:Conn_01x04", "J", "Fan (PicoBlade)", {"Pin_1": "GND", "Pin_2": "+5V", "Pin_3": "FAN_TACH_K", "Pin_4": "FAN_PWM"},
        "Connector_Molex:Molex_PicoBlade_53047-0410_1x04_P1.25mm_Vertical", dx=8)
k.R(cv, g, "100R", "FAN_PWM_3V3", "FAN_PWM"); k.R(cv, g, "10k", "FAN_PWM", "GND")
k.R(cv, g, "10k", "+3V3", "FAN_TACH"); k.R(cv, g, "10k", "FAN_TACH_K", "FAN_TACH"); k.C(cv, g, "1n", "FAN_TACH")
k.C(cv, g, "10u 10V", "+5V", fp=C0805)

cv.metin("KURTARMA / YAZILIM YUKLEME USB'si (Type-C, Jetson USB0, aygit kipi): Jetson'a ilk yazilim bu porttan yuklenir. VBUS gelince", 30, 250)
cv.metin("transistor GPIO00'i dusuge ceker (bilgisayar bagli). CC uclarinda 5k1: kart tuketicidir. VBUS karti beslemez.", 30, 256)
g = Izgara(50, 300, sutun=12)
k.parca(cv, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C (kurtarma)", {"VBUS": "USB_VBUS", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2",
        "D+": "USB0_DP", "D-": "USB0_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
k.koy(cv, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "USB0_DP", "6": "USB0_DP", "3": "USB0_DM", "4": "USB0_DM", "5": "USB_VBUS", "2": "GND"}, "Package_TO_SOT_SMD:SOT-666")
k.R(cv, g, "5k1 1%", "USB_CC1", "GND"); k.R(cv, g, "5k1 1%", "USB_CC2", "GND"); k.C(cv, g, "1u 25V", "USB_VBUS", fp=C0603)
k.R(cv, g, "100k", "USB_VBUS", "USB_VBUS_G"); k.R(cv, g, "100k", "USB_VBUS_G", "GND")
x, y = g.yer()
k.koy(cv, N7002[0], N7002[1], N7002[2], x, y, {"D": "USB0_VBUS_DET_N", "S": "GND", "G": "USB_VBUS_G"}, N7002[3])
k.bayrak(cv, g, "USB_VBUS")
cv.yaz(os.path.join(BURASI, "cevre.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_vision.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gc, jt, et, cv], {"operfly": ORTAK_URI})
print("yazildi: operfly_vision (kok + 5 sayfa)")
