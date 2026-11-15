"""Operfly Core şematiğini üretir. Çalıştırma: depo kökünden `python 01_DONANIM/CORE/kicad/uret.py`.

Kaynaklar: bu dosya ve ../pin_atamalari.csv. Çıktılar (*.kicad_sch) elle düzenlenmez.
Bağlantılar telle değil ağ etiketleriyle kurulur: aynı adı taşıyan etiketler aynı ağdır.
"""
import csv
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from sema_uret import Sema, kicad_sembol_dizini, kutuphane_tablolari  # noqa: E402

ORTAK = os.path.join(KOK, "01_DONANIM", "ORTAK_KUTUPHANE", "semboller", "operfly.kicad_sym")
BURASI = os.path.dirname(os.path.abspath(__file__))
KICAD = kicad_sembol_dizini()
P, T = "operfly_core", "2026-11-15"

# Ayak izleri
C0402, C0603, C0805, C1206 = ("Capacitor_SMD:C_%s" % x for x in ("0402_1005Metric", "0603_1608Metric", "0805_2012Metric", "1206_3216Metric"))
R0402 = "Resistor_SMD:R_0402_1005Metric"
FB0603 = "Inductor_SMD:L_0603_1608Metric"
XAL = "Inductor_SMD:L_Coilcraft_XAL4020-XXX"

sayac = {}


def ref(onek):
    sayac[onek] = sayac.get(onek, 0) + 1
    return "%s%d" % (onek, sayac[onek])


def lib(sema, ad):
    """'Kutuphane:Sembol' adını yükler (her sayfada bir kez)."""
    k, s = ad.split(":", 1)
    lid = "%s:%s" % (k, s)
    if lid not in sema.lib:
        sema.kutuphane(k, os.path.join(KICAD, k + ".kicad_sym"), s)
    return lid


class Izgara:
    """Küçük elemanları satır satır dizer."""

    def __init__(self, x, y, dx=22.86, dy=27.94, sutun=10):
        self.x0, self.y0, self.dx, self.dy, self.sutun, self.i = x, y, dx, dy, sutun, 0

    def yer(self):
        x, y = self.x0 + (self.i % self.sutun) * self.dx, self.y0 + (self.i // self.sutun) * self.dy
        self.i += 1
        return x, y

    def satir(self):
        self.i = ((self.i + self.sutun - 1) // self.sutun) * self.sutun


def iki(sema, g, sembol, onek, deger, a, b, fp, dnp=False):
    """İki uçlu eleman: 1. uç a ağına, 2. uç b ağına. dnp: karta dizilmez (yeri hazır)."""
    x, y = g.yer()
    r = ref(onek)
    sema.koy(lib(sema, sembol), r, deger + (" DNP" if dnp else ""), x, y, {"1": a, "2": b}, footprint=fp, dnp=dnp)
    return r


def C(sema, g, deger, a, b="GND", fp=C0402, dnp=False):
    return iki(sema, g, "Device:C", "C", deger, a, b, fp, dnp)


def R(sema, g, deger, a, b, fp=R0402, dnp=False):
    return iki(sema, g, "Device:R", "R", deger, a, b, fp, dnp)


def parca(sema, g, sembol, onek, deger, aglar, fp, bosluk=1, dx=10):
    """Çok uçlu eleman; ızgarada 1 + bosluk hücre kaplar."""
    x, y = g.yer()
    for _ in range(bosluk):
        g.yer()
    r = ref(onek)
    sema.koy(lib(sema, sembol), r, deger, x + dx, y, aglar, footprint=fp)
    return r


kok = Sema(P, "Operfly Core", kagit="A3", tarih=T)
kok.metin("Operfly Core - ucus kontrol karti (OPFCOR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/CORE/kicad/uret.py", 25.4, 33.02, 1.6)

# --- Sayfa 2: omurga portlari -------------------------------------------------
om = Sema(P, "Operfly Core - omurga portlari", kagit="A3", tarih=T, ust=kok, ad="Omurga", genel_etiket=True)
kok.alt_sayfa(om, "omurga.kicad_sch", 25.4, 50.8)
bus = om.kutuphane("operfly", ORTAK, "Operfly_Bus_20")
# Port 1: tam omurga. Core 100 Mbit calisir: yalnizca A ve B ciftleri kullanilir.
port1 = {"+12V": "+12V_BUS1", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L",
         "PPS": "PPS_BUS", "ETH_A+": "ETH_TX+", "ETH_A-": "ETH_TX-", "ETH_B+": "ETH_RX+", "ETH_B-": "ETH_RX-"}
# Port 2: yedek guc ve CAN; Ethernet ve PPS bagli degil (karar: 15 Kasim 2026).
port2 = {"+12V": "+12V_BUS2", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L"}
ref("J"), ref("J")
om.koy(bus, "J1", "Operfly Bus 1", 80, 90, port1, footprint="Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical")
om.koy(bus, "J2", "Operfly Bus 2 (yedek)", 190, 90, port2, footprint="Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical")
om.metin("Port 1: tam omurga. Port 2: yedek guc ve CAN.", 40, 40)
om.yaz(os.path.join(BURASI, "omurga.kicad_sch"))

# --- Sayfa 3: islemci ---------------------------------------------------------
mcu = Sema(P, "Operfly Core - islemci (STM32H753IIK6)", kagit="A1", tarih=T, ust=kok, ad="Islemci", genel_etiket=True)
kok.alt_sayfa(mcu, "islemci.kicad_sch", 101.6, 50.8)
h7 = lib(mcu, "MCU_ST_STM32H7:STM32H753IIKx")
adlar = {}
for no, ad, _x, _y, _a in mcu.pinler[h7]:
    adlar.setdefault(ad.split("-")[0] if ad.startswith("P") and ad != "PDR_ON" else ad, []).append(no)
aglar = {}
for satir in csv.DictReader(open(os.path.join(BURASI, "..", "pin_atamalari.csv"), encoding="utf-8"), delimiter=";"):
    (top,) = adlar[satir["pin"]]
    aglar[top] = satir["sinyal"]
guc = {"VDD": "+3V3", "VDD33_USB": "+3V3", "VSS": "GND", "VSSA": "GND", "VREF-": "GND", "VDDA": "+3V3A", "VREF+": "VREF",
       "VBAT": "VBAT", "NRST": "MCU_NRST", "BOOT0": "MCU_BOOT0",
       "PDR_ON": "+3V3"}   # PDR_ON: dahili besleme gozetimi acik
for ad, ag in guc.items():
    for top in adlar[ad]:
        aglar[top] = ag
for i, top in enumerate(sorted(adlar["VCAP"]), 1):
    aglar[top] = "VCAP%d" % i   # her VCAP pinine ayri kondansator
ref("U")
mcu.koy(h7, "U1", "STM32H753IIK6", 420, 300, aglar, footprint="Package_BGA:UFBGA-201_10x10mm_Layout15x15_P0.65mm")
mcu.metin("Pin atamalari: 01_DONANIM/CORE/pin_atamalari.csv. Etiketsiz pinler bostur.", 40, 30)
mcu.yaz(os.path.join(BURASI, "islemci.kicad_sch"))

# --- Sayfa 4: guc -------------------------------------------------------------
gc = Sema(P, "Operfly Core - guc", kagit="A2", tarih=T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gc, "guc.kicad_sch", 177.8, 50.8)

gc.metin("GIRIS: iki omurga portu diyotla birlestirilir (+12V_IN). Asiri gerilim diyotu 18 V.", 30, 30)
g = Izgara(40, 55)
iki(gc, g, "Device:D_Schottky", "D", "B360A (60 V, 3 A)", "+12V_IN", "+12V_BUS1", "Diode_SMD:D_SMA")
iki(gc, g, "Device:D_Schottky", "D", "B360A (60 V, 3 A)", "+12V_IN", "+12V_BUS2", "Diode_SMD:D_SMA")
iki(gc, g, "Device:D_TVS", "D", "SMBJ18A", "+12V_IN", "GND", "Diode_SMD:D_SMB")
C(gc, g, "10u 50V", "+12V_IN", fp=C1206)
C(gc, g, "100n 50V", "+12V_IN", fp=C0603)
for ag in ("+12V_BUS1", "+12V_BUS2", "+12V_IN", "GND"):
    gc.bayrak(ag, *g.yer(), KICAD)

gc.metin("5 V: AP63205 (sabit 5 V, 2 A, 1,1 MHz). Degerler uretici ornek devresinden: L 4,7 uH, cikis 2 x 22 uF.", 30, 100)
g = Izgara(40, 125)
x, y = g.yer(); g.yer()
gc.koy(lib(gc, "Regulator_Switching:AP63205WU"), ref("U"), "AP63205QWU", x + 10, y,
       {"IN": "+12V_IN", "EN": "EN_5V", "GND": "GND", "SW": "SW_5V", "BST": "BST_5V", "FB": "+5V"}, footprint="Package_TO_SOT_SMD:TSOT-23-6")
R(gc, g, "100k", "+12V_IN", "EN_5V")
C(gc, g, "10u 50V", "+12V_IN", fp=C1206)
C(gc, g, "100n", "BST_5V", "SW_5V")
iki(gc, g, "Device:L", "L", "4u7 XAL4020-472", "SW_5V", "+5V", XAL)
C(gc, g, "22u 16V", "+5V", fp=C1206)
C(gc, g, "22u 16V", "+5V", fp=C1206)
gc.bayrak("+5V", *g.yer(), KICAD)

gc.metin("3,3 V: AP63203 (sabit 3,3 V, 2 A). L 3,3 uH, cikis 2 x 22 uF. 12 V'tan dogrudan beslenir.", 30, 170)
g = Izgara(40, 195)
x, y = g.yer(); g.yer()
gc.koy(lib(gc, "Regulator_Switching:AP63203WU"), ref("U"), "AP63203QWU", x + 10, y,
       {"IN": "+12V_IN", "EN": "EN_3V3", "GND": "GND", "SW": "SW_3V3", "BST": "BST_3V3", "FB": "+3V3"}, footprint="Package_TO_SOT_SMD:TSOT-23-6")
R(gc, g, "100k", "+12V_IN", "EN_3V3")
C(gc, g, "10u 50V", "+12V_IN", fp=C1206)
C(gc, g, "100n", "BST_3V3", "SW_3V3")
iki(gc, g, "Device:L", "L", "3u3 XAL4020-332", "SW_3V3", "+3V3", XAL)
C(gc, g, "22u 16V", "+3V3", fp=C1206)
C(gc, g, "22u 16V", "+3V3", fp=C1206)
gc.bayrak("+3V3", *g.yer(), KICAD)

gc.metin("SENSOR BESLEMELERI: her IMU icin ayri, islemciden acilip kapatilan dusuk gurultulu regulator (LP5907-3.3).", 30, 240)
g = Izgara(40, 265, sutun=5)
for n in (1, 2, 3):
    x, y = g.yer()
    gc.koy(lib(gc, "Regulator_Linear:LP5907MFX-3.3"), ref("U"), "LP5907MFX-3.3", x + 5, y,
           {"IN": "+5V", "EN": "SENS%d_EN" % n, "GND": "GND", "OUT": "+3V3_S%d" % n}, footprint="Package_TO_SOT_SMD:SOT-23-5")
    C(gc, g, "1u", "+5V")
    C(gc, g, "1u", "+3V3_S%d" % n)
    R(gc, g, "100k", "SENS%d_EN" % n, "GND")
    g.satir()

gc.metin("ANALOG BESLEME ve REFERANS: +3V3A ferrit uzerinden, VREF 10 ohm uzerinden. VBAT +3V3'e bagli (yedek pil yok).", 330, 30)
g = Izgara(340, 55)
iki(gc, g, "Device:FerriteBead", "FB", "BLM18PG221", "+3V3", "+3V3A", FB0603)
C(gc, g, "1u", "+3V3A")
C(gc, g, "100n", "+3V3A")
R(gc, g, "10R", "+3V3A", "VREF")
C(gc, g, "1u", "VREF")
C(gc, g, "100n", "VREF")
R(gc, g, "0R", "+3V3", "VBAT")
C(gc, g, "100n", "VBAT")
for ag in ("+3V3A", "VREF", "VBAT"):
    gc.bayrak(ag, *g.yer(), KICAD)

gc.metin("OLCUM BOLUCULERI: 12 V icin 11:1, 5 V ve sensor beslemesi icin 2:1. PGOOD_5V: 5 V varken yuksek.", 330, 125)
g = Izgara(340, 150)
R(gc, g, "100k", "+12V_IN", "V12_BUS_SENS"); R(gc, g, "10k", "V12_BUS_SENS", "GND"); C(gc, g, "100n", "V12_BUS_SENS")
R(gc, g, "10k", "+5V", "V5_SENS"); R(gc, g, "10k", "V5_SENS", "GND"); C(gc, g, "100n", "V5_SENS")
R(gc, g, "10k", "+3V3_S1", "V3V3_SENS"); R(gc, g, "10k", "V3V3_SENS", "GND"); C(gc, g, "100n", "V3V3_SENS")
g.satir()
R(gc, g, "10k", "+5V", "PGOOD_5V"); R(gc, g, "18k", "PGOOD_5V", "GND")
gc.yaz(os.path.join(BURASI, "guc.kicad_sch"))

# --- Sayfa 5: islemci destek devreleri ---------------------------------------
ds = Sema(P, "Operfly Core - saat, sifirlama ve ayirma kondansatorleri", kagit="A2", tarih=T, ust=kok, ad="Islemci_Destek", genel_etiket=True)
kok.alt_sayfa(ds, "islemci_destek.kicad_sch", 254.0, 50.8)

ds.metin("ANA KRISTAL 16 MHz (3225, CL 8 pF) ve SAAT KRISTALI 32,768 kHz. Yuk kondansatorleri kristal secilince dogrulanacak.", 30, 30)
g = Izgara(40, 55)
x, y = g.yer()
ds.koy(lib(ds, "Device:Crystal_GND24"), ref("Y"), "16 MHz", x, y, {"1": "HSE_IN", "3": "HSE_OUT", "2": "GND", "4": "GND"}, footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
C(ds, g, "10p", "HSE_IN"); C(ds, g, "10p", "HSE_OUT")
x, y = g.yer()
ds.koy(lib(ds, "Device:Crystal"), ref("Y"), "32.768 kHz", x, y, {"1": "LSE_IN", "2": "LSE_OUT"}, footprint="Crystal:Crystal_SMD_3215-2Pin_3.2x1.5mm")
C(ds, g, "6p8", "LSE_IN"); C(ds, g, "6p8", "LSE_OUT")

ds.metin("SIFIRLAMA ve ACILIS: NRST'de 100 nF ve 10 k yukari cekme; BOOT0 10 k ile asagi cekili (normal acilis).", 30, 100)
g = Izgara(40, 125)
R(ds, g, "10k", "+3V3", "MCU_NRST"); C(ds, g, "100n", "MCU_NRST"); R(ds, g, "10k", "MCU_BOOT0", "GND")

ds.metin("AYIRMA KONDANSATORLERI: her VDD topuna 100 nF (13 adet) + govde kondansatorleri; VCAP pinlerine 2,2 uF.", 30, 170)
g = Izgara(40, 195, sutun=14)
for _ in range(13):
    C(ds, g, "100n", "+3V3")
C(ds, g, "100n", "+3V3")   # VDD33_USB
g.satir()
C(ds, g, "4u7", "+3V3", fp=C0603); C(ds, g, "10u", "+3V3", fp=C0805); C(ds, g, "10u", "+3V3", fp=C0805); C(ds, g, "1u", "+3V3")
C(ds, g, "2u2", "VCAP1", fp=C0603); C(ds, g, "2u2", "VCAP2", fp=C0603)
ds.yaz(os.path.join(BURASI, "islemci_destek.kicad_sch"))

# --- Sayfa 6: haberlesme (Ethernet, CAN FD, USB, microSD, PPS) ---------------
hb = Sema(P, "Operfly Core - Ethernet, CAN FD, USB, microSD, PPS", kagit="A1", tarih=T, ust=kok, ad="Haberlesme", genel_etiket=True)
kok.alt_sayfa(hb, "haberlesme.kicad_sch", 25.4, 101.6)

hb.metin("ETHERNET 100 Mbit (RMII): LAN8742A. 50 MHz osilator hem alici-vericiyi hem islemciyi besler (PTP icin tek saat kaynagi).", 30, 30)
hb.metin("Acilis ayarlari ic direnclerle: adres 0, otomatik anlasma, kesme cikisi etkin, ic 1,2 V regulator acik.", 30, 36)
g = Izgara(50, 80, sutun=16)
parca(hb, g, "Interface_Ethernet:LAN8742A", "U", "LAN8742A-CZ", {
    "VDD1A": "+3V3_PHY", "VDD2A": "+3V3_PHY", "VDDIO": "+3V3", "VDDCR": "VDDCR_PHY", "VSS": "GND",
    "TXD0": "ETH_TXD0", "TXD1": "ETH_TXD1", "TXEN": "ETH_TX_EN",
    "RXD0/MODE0": "ETH_RXD0", "RXD1/MODE1": "ETH_RXD1", "CRS_DV/MODE2": "ETH_CRS_DV",
    "MDIO": "ETH_MDIO", "MDC": "ETH_MDC", "~{RST}": "PHY_NRST", "~{INT}/REFCLKO": "PHY_INT",
    "XTAL1/CLKIN": "PHY_CLKIN", "RBIAS": "PHY_RBIAS",
    "TXP": "PHY_TXP", "TXN": "PHY_TXN", "RXP": "PHY_RXP", "RXN": "PHY_RXN",
}, "Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.5x2.5mm_ThermalVias", bosluk=3, dx=30)
parca(hb, g, "Transformer:PT61017PEL", "T", "PT61017PEL (10/100, 1:1)", {
    "TD+": "PHY_TXP", "TD-": "PHY_TXN", "C_TD": "+3V3_PHY", "RD+": "PHY_RXP", "RD-": "PHY_RXN", "C_RD": "+3V3_PHY",
    "TX+": "ETH_TX+", "TX-": "ETH_TX-", "C_TX": "ETH_CT_TX", "RX+": "ETH_RX+", "RX-": "ETH_RX-", "C_RX": "ETH_CT_RX",
}, "Transformer_SMD:Transformer_Ethernet_Bourns_PT61017PEL", bosluk=2, dx=25)
parca(hb, g, "Oscillator:ASE-xxxMHz", "Y", "50 MHz 25 ppm", {"EN": "+3V3", "Vdd": "+3V3", "GND": "GND", "OUT": "CLK50"},
      "Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm", bosluk=1, dx=15)
R(hb, g, "33R", "CLK50", "PHY_CLKIN"); R(hb, g, "33R", "CLK50", "ETH_REF_CLK"); C(hb, g, "100n", "+3V3")
g.satir()
g = Izgara(50, 140, sutun=16)
for ag in ("PHY_TXP", "PHY_TXN", "PHY_RXP", "PHY_RXN"):
    R(hb, g, "49R9 1%", "+3V3_PHY", ag)
R(hb, g, "12k1 1%", "PHY_RBIAS", "GND")
R(hb, g, "1k5", "+3V3", "ETH_MDIO"); R(hb, g, "10k", "+3V3", "PHY_INT"); R(hb, g, "10k", "PHY_NRST", "GND")
R(hb, g, "75R", "ETH_CT_TX", "ETH_BS"); R(hb, g, "75R", "ETH_CT_RX", "ETH_BS"); C(hb, g, "1n 2kV", "ETH_BS", fp=C1206)
g.satir()
iki(hb, g, "Device:FerriteBead", "FB", "BLM18PG221", "+3V3", "+3V3_PHY", FB0603)
C(hb, g, "10u", "+3V3_PHY", fp=C0805); C(hb, g, "100n", "+3V3_PHY"); C(hb, g, "100n", "+3V3_PHY"); C(hb, g, "100n", "+3V3_PHY")
C(hb, g, "100n", "+3V3"); C(hb, g, "1u", "VDDCR_PHY"); C(hb, g, "470p", "VDDCR_PHY")
hb.bayrak("+3V3_PHY", *g.yer(), KICAD); hb.bayrak("VDDCR_PHY", *g.yer(), KICAD)

hb.metin("CAN FD: iki bagimsiz alici-verici (TJA1051-3, 5 Mbit/s). Sessiz mod girisi (S) asagi cekili: islemci sifirlanirken hat dinlenir, surulmez.", 30, 215)
hb.metin("Sonlandirma direncleri dizilmez (DNP): omurga yildiz baglantili, sonlandirma Hub'dadir.", 30, 221)
g = Izgara(50, 250, sutun=16)
for h in ("A", "B"):
    parca(hb, g, "Interface_CAN_LIN:TJA1051TK-3", "U", "TJA1051TK/3", {
        "TXD": "CAN_%s_TX" % h, "RXD": "CAN_%s_RX" % h, "S": "CAN_%s_STB" % h, "VCC": "+5V", "VIO": "+3V3", "GND": "GND",
        "CANH": "CAN_%s_H" % h, "CANL": "CAN_%s_L" % h}, "Package_SON:HVSON-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm", bosluk=1, dx=15)
    C(hb, g, "100n", "+5V"); C(hb, g, "100n", "+3V3"); R(hb, g, "10k", "CAN_%s_STB" % h, "GND")
    x, y = g.yer()
    hb.koy(lib(hb, "Power_Protection:NUP2105L"), ref("D"), "NUP2105L", x, y, {"1": "CAN_%s_H" % h, "2": "CAN_%s_L" % h, "3": "GND"}, footprint="Package_TO_SOT_SMD:SOT-23")
    R(hb, g, "60R4", "CAN_%s_H" % h, "CAN_%s_TERM" % h, dnp=True); R(hb, g, "60R4", "CAN_%s_L" % h, "CAN_%s_TERM" % h, dnp=True)
    C(hb, g, "4n7", "CAN_%s_TERM" % h, dnp=True)
    g.satir()

hb.metin("USB (servis portu, Type-C, yalnizca veri): karti beslemez; VBUS yalnizca 'bilgisayar bagli' bilgisini verir.", 430, 30)
g = Izgara(450, 85, sutun=12)
parca(hb, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C", {
    "VBUS": "VBUS_USB", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2", "D+": "USB_DP", "D-": "USB_DM"},
    "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
hb.koy(lib(hb, "Power_Protection:USBLC6-2P6"), ref("D"), "USBLC6-2P6", x + 10, y,
       {"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "5": "VBUS_USB", "2": "GND"}, footprint="Package_TO_SOT_SMD:SOT-666")
R(hb, g, "5k1", "USB_CC1", "GND"); R(hb, g, "5k1", "USB_CC2", "GND")
R(hb, g, "10k", "VBUS_USB", "USB_VBUS"); R(hb, g, "15k", "USB_VBUS", "GND"); C(hb, g, "100n", "USB_VBUS"); C(hb, g, "1u 16V", "VBUS_USB", fp=C0603)

hb.metin("microSD (ucus kaydi): 4 bit SDMMC. Kart algilama anahtari kart takiliyken SD_DET'i sifira ceker.", 430, 150)
g = Izgara(450, 195, sutun=12)
parca(hb, g, "Connector:Micro_SD_Card_Det_Hirose_DM3AT", "J", "microSD DM3AT-SF-PEJM5", {
    "DAT0": "SD_D0", "DAT1": "SD_D1", "DAT2": "SD_D2", "DAT3/CD": "SD_D3", "CMD": "SD_CMD", "CLK": "SD_CK_R",
    "VDD": "+3V3", "VSS": "GND", "DET_A": "SD_DET", "DET_B": "GND", "SHIELD": "GND"},
    "Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5", bosluk=3, dx=35)
R(hb, g, "33R", "SD_CK", "SD_CK_R")
for ag in ("SD_D0", "SD_D1", "SD_D2", "SD_D3", "SD_CMD"):
    R(hb, g, "47k", "+3V3", ag)
R(hb, g, "10k", "+3V3", "SD_DET")
g.satir()
C(hb, g, "10u", "+3V3", fp=C0805); C(hb, g, "100n", "+3V3")

hb.metin("PPS: omurgadan gelen saniye darbesi (3,3 V lojik, 5 V'a dayanikli) tetikleyicili tamponla islemciye girer.", 430, 270)
g = Izgara(450, 300, sutun=12)
x, y = g.yer(); g.yer()
hb.koy(lib(hb, "74xGxx:74LVC1G17"), ref("U"), "74LVC1G17", x + 15, y, {"2": "PPS_BUF_IN", "4": "PPS_IN", "5": "+3V3", "3": "GND"},
       footprint="Package_TO_SOT_SMD:SOT-353_SC-70-5")
R(hb, g, "100R", "PPS_BUS", "PPS_BUF_IN"); R(hb, g, "100k", "PPS_BUF_IN", "GND"); C(hb, g, "100n", "+3V3")
x, y = g.yer()
hb.koy(lib(hb, "Connector:TestPoint"), ref("TP"), "ETH_PPS_OUT", x, y, {"1": "ETH_PPS_OUT"}, footprint="TestPoint:TestPoint_Pad_D1.0mm")
hb.yaz(os.path.join(BURASI, "haberlesme.kicad_sch"))

# --- Sayfa 7: sensorler, bellek, guvenli eleman, LED, hata ayiklama -----------
sn = Sema(P, "Operfly Core - sensorler, bellek, guvenli eleman, hata ayiklama", kagit="A1", tarih=T, ust=kok, ad="Sensorler", genel_etiket=True)
kok.alt_sayfa(sn, "sensorler.kicad_sch", 101.6, 101.6)


def op(sema, ad):
    lid = "operfly:" + ad
    if lid not in sema.lib:
        sema.kutuphane("operfly", ORTAK, ad)
    return lid


sn.metin("IMU 1 (ICM-42688-P, SPI1) - besleme +3V3_S1. Ayni beslemede barometre 1 ve pusula.", 30, 30)
g = Izgara(50, 70, sutun=16)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(op(sn, "ICM-42688-P"), ref("U"), "ICM-42688-P", x + 25, y, {
    "AP_CS": "IMU1_CS", "AP_SCLK": "IMU1_SCK", "AP_SDI": "IMU1_MOSI", "AP_SDO": "IMU1_MISO", "INT1": "IMU1_DRDY",
    "VDD": "+3V3_S1", "VDDIO": "+3V3_S1", "GND": "GND", "RESV7": "GND", "RESV11": "GND"}, footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm")
C(sn, g, "100n", "+3V3_S1"); C(sn, g, "100n", "+3V3_S1"); C(sn, g, "2u2", "+3V3_S1", fp=C0603); R(sn, g, "10k", "+3V3_S1", "IMU1_CS")

sn.metin("IMU 2 (BMI088, SPI2) - besleme +3V3_S2. Ivmeolcer ve donuolcer ayri secme ve kesme hatlarina sahip.", 30, 115)
g = Izgara(50, 160, sutun=16)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(lib(sn, "Sensor_Motion:BMI088"), ref("U"), "BMI088", x + 25, y, {
    "~{CSB1}": "IMU2_CS_ACC", "~{CSB2}": "IMU2_CS_GYR", "SCK/SCL": "IMU2_SCK", "SDI/SDA": "IMU2_MOSI", "SDO1": "IMU2_SDO_ACC", "SDO2": "IMU2_SDO_GYR",
    "INT1": "IMU2_INT_ACC", "INT3": "IMU2_INT_GYR", "PS": "GND", "VDD": "+3V3_S2", "VDDIO": "+3V3_S2", "GNDA": "GND", "GNDIO": "GND"},
    footprint="Package_LGA:Bosch_LGA-16_4.5x3mm_P0.5mm_LayoutBorder7x1y_ClockwisePinNumbering")
R(sn, g, "33R", "IMU2_SDO_ACC", "IMU2_MISO"); R(sn, g, "33R", "IMU2_SDO_GYR", "IMU2_MISO")
C(sn, g, "100n", "+3V3_S2"); C(sn, g, "100n", "+3V3_S2"); C(sn, g, "2u2", "+3V3_S2", fp=C0603)
R(sn, g, "10k", "+3V3_S2", "IMU2_CS_ACC"); R(sn, g, "10k", "+3V3_S2", "IMU2_CS_GYR")

sn.metin("IMU 3 (ICM-45686, SPI4) - besleme +3V3_S3.", 30, 210)
g = Izgara(50, 250, sutun=16)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(op(sn, "ICM-45686"), ref("U"), "ICM-45686", x + 25, y, {
    "AP_CS": "IMU3_CS", "AP_SCLK": "IMU3_SCK", "AP_SDI": "IMU3_MOSI", "AP_SDO": "IMU3_MISO", "INT1": "IMU3_DRDY",
    "VDD": "+3V3_S3", "VDDIO": "+3V3_S3", "GND": "GND"}, footprint="Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm")
C(sn, g, "100n", "+3V3_S3"); C(sn, g, "100n", "+3V3_S3"); C(sn, g, "2u2", "+3V3_S3", fp=C0603); R(sn, g, "10k", "+3V3_S3", "IMU3_CS")

sn.metin("I2C A: barometre 1 (BMP390, adres 0x76), pusula (IST8310), guvenli eleman (SE050). I2C B: barometre 2 (MS5611, adres 0x77).", 30, 300)
g = Izgara(50, 345, sutun=16)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(op(sn, "BMP390"), ref("U"), "BMP390", x + 20, y, {"SCK": "I2C_A_SCL", "SDI": "I2C_A_SDA", "SDO": "GND", "CSB": "+3V3_S1",
       "VDD": "+3V3_S1", "VDDIO": "+3V3_S1", "VSS": "GND"}, footprint="Package_LGA:ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y")
C(sn, g, "100n", "+3V3_S1"); C(sn, g, "100n", "+3V3_S1")
x, y = g.yer(); g.yer(); g.yer()
sn.koy(lib(sn, "Sensor_Magnetic:IST8310"), ref("U"), "IST8310", x + 20, y, {"SCL": "I2C_A_SCL", "SDA": "I2C_A_SDA", "AVDD": "+3V3_S1", "DVDD": "+3V3_S1",
       "VSS": "GND", "C1": "MAG_C1", "~{RST}": "+3V3_S1", "CAD0": "GND", "CAD1": "GND"}, footprint="Package_LGA:LGA-16_3x3mm_P0.5mm")
C(sn, g, "4u7", "MAG_C1", fp=C0603); C(sn, g, "100n", "+3V3_S1"); C(sn, g, "100n", "+3V3_S1")
g.satir()
g = Izgara(50, 410, sutun=16)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(lib(sn, "Sensor_Pressure:MS5611-01BA"), ref("U"), "MS5611-01BA03", x + 20, y, {"SCLK": "I2C_B_SCL", "SDI/SDA": "I2C_B_SDA", "PS": "+3V3_S2", "CSB": "GND",
       "VDD": "+3V3_S2", "GND": "GND"}, footprint="Package_LGA:LGA-8_3x5mm_P1.25mm")
C(sn, g, "100n", "+3V3_S2")
for ag in ("I2C_A_SCL", "I2C_A_SDA", "I2C_B_SCL", "I2C_B_SDA"):
    R(sn, g, "2k2", "+3V3", ag)

sn.metin("GUVENLI ELEMAN (SE050): SE_NRST hatti ENA girisini surer; sifira cekilince eleman kapanir, birakilinca yeniden baslar.", 430, 30)
g = Izgara(450, 80, sutun=12)
x, y = g.yer(); g.yer(); g.yer()
sn.koy(op(sn, "SE050"), ref("U"), "SE050E2HQ1", x + 20, y, {"I2C_SDA": "I2C_A_SDA", "I2C_SCL": "I2C_A_SCL", "ENA": "SE_NRST",
       "VIN": "+3V3", "VCC": "SE_VCC", "VOUT": "SE_VCC", "VSS": "GND", "EP": "GND"}, footprint="Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm")
R(sn, g, "10k", "+3V3", "SE_NRST"); C(sn, g, "100n", "+3V3"); C(sn, g, "2u2", "SE_VCC", fp=C0603)

sn.metin("FRAM (parametre ve durum bellegi, SPI5).", 430, 140)
g = Izgara(450, 180, sutun=12)
x, y = g.yer(); g.yer()
sn.koy(lib(sn, "Memory_NVRAM:MB85RS2MT"), ref("U"), "FM25V10-G", x + 15, y, {"~{CS}": "FRAM_CS", "SO": "FRAM_MISO", "SI": "FRAM_MOSI", "SCK": "FRAM_SCK",
       "~{WP}": "+3V3", "~{HOLD}": "+3V3", "VDD": "+3V3", "GND": "GND"}, footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm")
R(sn, g, "10k", "+3V3", "FRAM_CS"); C(sn, g, "100n", "+3V3")

sn.metin("DURUM LED'leri (sifirda yanar), kart surum direncleri, hata ayiklama baglantisi ve olcum noktalari.", 430, 230)
g = Izgara(450, 270, sutun=12)
for renk, ag in (("kirmizi", "LED_R"), ("yesil", "LED_G"), ("mavi", "LED_B")):
    iki(sn, g, "Device:LED", "D", "LED " + renk, ag, "LED_%s_A" % renk[0].upper(), "LED_SMD:LED_0603_1608Metric")
    R(sn, g, "1k", "+3V3", "LED_%s_A" % renk[0].upper())
g.satir()
R(sn, g, "10k", "+3V3A", "HW_VER"); R(sn, g, "10k", "HW_VER", "GND"); R(sn, g, "10k", "+3V3A", "HW_REV"); R(sn, g, "1k", "HW_REV", "GND")
g.satir()
x, y = g.yer(); g.yer(); g.yer()
sn.koy(lib(sn, "Connector:Conn_ARM_JTAG_SWD_10"), ref("J"), "SWD 2x5 1,27 mm", x + 15, y + 10, {"VTref": "+3V3", "GND": "GND", "GNDDetect": "GND",
       "SWDIO/TMS": "SWDIO", "SWCLK/TCK": "SWCLK", "SWO/TDO": "SWO", "~{RESET}": "MCU_NRST"}, footprint="Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD")
for ag in ("DBG_UART_TX", "DBG_UART_RX"):
    x, y = g.yer()
    sn.koy(lib(sn, "Connector:TestPoint"), ref("TP"), ag, x, y, {"1": ag}, footprint="TestPoint:TestPoint_Pad_D1.0mm")
sn.yaz(os.path.join(BURASI, "sensorler.kicad_sch"))

# --- Sayfa 8: IO/failsafe islemcisi ve cikislar -------------------------------
io = Sema(P, "Operfly Core - IO/failsafe islemcisi ve cikislar", kagit="A1", tarih=T, ust=kok, ad="IO", genel_etiket=True)
kok.alt_sayfa(io, "io.kicad_sch", 177.8, 101.6)
io.metin("IO/FAILSAFE ISLEMCISI (STM32G0B1CET6): kendi 3,3 V regulatoru, kendi kristali, kendi CAN alici-vericisi (CAN B).", 30, 30)
io.metin("Ana islemciyle arasindaki hatlar seri direnclidir: biri beslemesizken digerini yuklemez.", 30, 36)
g0 = lib(io, "MCU_ST_STM32G0:STM32G0B1CETx")
ioag = {}
for satir in csv.DictReader(open(os.path.join(BURASI, "..", "io_pin_atamalari.csv"), encoding="utf-8"), delimiter=";"):
    ioag[satir["pin"]] = satir["sinyal"]
ioag.update({"VDD": "+3V3_IO", "VBAT": "+3V3_IO", "VREF+": "+3V3_IO", "VSS": "GND"})
eksik = set(ioag) - {ad for _no, ad, _x, _y, _a in io.pinler[g0]}
assert not eksik, eksik
io.koy(g0, ref("U"), "STM32G0B1CET6", 110, 130, ioag, footprint="Package_QFP:LQFP-48_7x7mm_P0.5mm")
g = Izgara(200, 70, sutun=14)
x, y = g.yer(); g.yer()
io.koy(lib(io, "Regulator_Linear:LP5907MFX-3.3"), ref("U"), "LP5907MFX-3.3", x + 10, y, {"IN": "+5V", "EN": "+5V", "GND": "GND", "OUT": "+3V3_IO"}, footprint="Package_TO_SOT_SMD:SOT-23-5")
C(io, g, "1u", "+5V"); C(io, g, "1u", "+3V3_IO"); C(io, g, "4u7", "+3V3_IO", fp=C0603); C(io, g, "100n", "+3V3_IO"); C(io, g, "100n", "+3V3_IO"); C(io, g, "100n", "+3V3_IO")
x, y = g.yer()
io.koy(lib(io, "Device:Crystal_GND24"), ref("Y"), "16 MHz", x, y, {"1": "IO_HSE_IN", "3": "IO_HSE_OUT", "2": "GND", "4": "GND"}, footprint="Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
C(io, g, "10p", "IO_HSE_IN"); C(io, g, "10p", "IO_HSE_OUT")
g.satir()
R(io, g, "10k", "+3V3_IO", "IO_NRST_PIN"); C(io, g, "100n", "IO_NRST_PIN"); R(io, g, "1k", "IO_NRST", "IO_NRST_PIN")
R(io, g, "10k", "IO_BOOT0", "IO_SWCLK"); R(io, g, "1k", "N_ARMED", "N_ARMED_IO"); R(io, g, "100k", "N_ARMED_IO", "+3V3_IO")
R(io, g, "10k", "IO_MUX_SEL", "GND"); R(io, g, "10k", "IO_CAN_S", "GND")
iki(io, g, "Device:LED", "D", "LED sari", "IO_LED", "IO_LED_A", "LED_SMD:LED_0603_1608Metric"); R(io, g, "1k", "+3V3_IO", "IO_LED_A")
for ag in ("IO_SWDIO", "IO_SWCLK"):
    x, y = g.yer()
    io.koy(lib(io, "Connector:TestPoint"), ref("TP"), ag, x, y, {"1": ag}, footprint="TestPoint:TestPoint_Pad_D1.0mm")
g.satir()
parca(io, g, "Interface_CAN_LIN:TJA1051TK-3", "U", "TJA1051TK/3", {"TXD": "IO_CAN_TX", "RXD": "IO_CAN_RX", "S": "IO_CAN_S", "VCC": "+5V", "VIO": "+3V3_IO", "GND": "GND",
      "CANH": "CAN_B_H", "CANL": "CAN_B_L"}, "Package_SON:HVSON-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm", bosluk=1, dx=15)
C(io, g, "100n", "+5V"); C(io, g, "100n", "+3V3_IO")

io.metin("CIKIS SECICI: 1-8. cikislar analog anahtardan gecer (iki yonlu sinyale uygun). SEL=0: ana islemci, SEL=1: IO islemcisi.", 30, 240)
io.metin("SEL asagi cekilidir: IO islemcisi calismiyorken cikislari ana islemci surer. 9-12. cikislar dogrudan ana islemcidendir.", 30, 246)
g = Izgara(60, 300, sutun=16)
for k in (0, 1):
    n = [k * 4 + i for i in (1, 2, 3, 4)]
    ag = {"SEL": "IO_MUX_SEL", "~{EN}": "GND", "VDD": "+5V", "GND": "GND"}
    for i, c in enumerate(n, 1):
        ag["S%dA" % i] = "OUT%d" % c; ag["S%dB" % i] = "IO_OUT%d" % c; ag["D%d" % i] = "OUT%d_M" % c
    parca(io, g, "Analog_Switch:TMUX1574PW", "U", "TMUX1574PW", ag, "Package_SO:TSSOP-16_4.4x5mm_P0.65mm", bosluk=2, dx=25)
    C(io, g, "100n", "+5V")
g.satir()
g = Izgara(60, 380, sutun=16)
for c in range(1, 13):
    R(io, g, "33R", "OUT%d_M" % c if c <= 8 else "OUT%d" % c, "CONN_OUT%d" % c)
kon = {"Pin_%d" % (2 * c - 1): "CONN_OUT%d" % c for c in range(1, 13)}
kon.update({"Pin_%d" % (2 * c): "GND" for c in range(1, 14)})
x, y = g.yer(); g.yer()
io.koy(lib(io, "Connector_Generic:Conn_02x13_Odd_Even"), ref("J"), "Cikis konnektoru 26 kontak", x + 20, y, kon, footprint="Connector_Harwin:Harwin_Gecko_G125-MS12605M2P_2x13_P1.25mm_Vertical")
io.metin("Konnektor: tek numarali kontaklar 1-12. cikis, cift numarali kontaklar GND, 25. kontak bos.", 30, 420)
io.yaz(os.path.join(BURASI, "io.kicad_sch"))

# --- Sayfa 9: gozetim (watchdog, guc kesintisi, enerji deposu) ve Peltier -----
gz = Sema(P, "Operfly Core - gozetim, enerji deposu, Peltier surucusu", kagit="A2", tarih=T, ust=kok, ad="Gozetim", genel_etiket=True)
kok.alt_sayfa(gz, "gozetim.kicad_sch", 254.0, 101.6)

gz.metin("HARICI WATCHDOG (TPS3430): ana islemci WDG_KICK hattini 30-50 ms'de bir dusurur. Darbe kesilirse FMU_FAULT_N 200 ms sifira iner;", 30, 30)
gz.metin("IO islemcisi bunu gorur ve cikislari devralir. Watchdog ana islemciyi SIFIRLAMAZ (kendi ic watchdog'u sifirlar). Besleme: +3V3_IO.", 30, 36)
g = Izgara(50, 80, sutun=12)
parca(gz, g, "Power_Supervisor:TPS3430WDRC", "U", "TPS3430WDRCR", {"VDD1": "+3V3_IO", "VDD2": "+3V3_IO", "GND": "GND", "CWD": "WDG_CWD", "SET0": "GND", "SET1": "GND",
      "WDI": "WDG_WDI", "~{WDO}": "FMU_FAULT_N"}, "Package_SON:VSON-10-1EP_3x3mm_P0.5mm_EP1.2x2mm", bosluk=2, dx=20)
R(gz, g, "10k", "+3V3_IO", "WDG_CWD"); R(gz, g, "1k", "WDG_KICK", "WDG_WDI"); R(gz, g, "100k", "WDG_WDI", "GND")
R(gz, g, "10k", "+3V3_IO", "FMU_FAULT_N"); C(gz, g, "100n", "+3V3_IO")
R(gz, g, "1k", "IO_FMU_RST", "MCU_NRST", dnp=True)

gz.metin("GUC KESINTISI ALGILAMA (TPS3808G01): giris 10,1 V altina inince PWR_FAIL_N sifira iner; islemci durumu FRAM'e yazar.", 30, 130)
gz.metin("ENERJI DEPOSU: 2 x 470 uF. Kesintiden sonra karti yaklasik 10-20 ms tasir (yuke bagli; olcumle dogrulanacak).", 30, 136)
g = Izgara(50, 175, sutun=12)
parca(gz, g, "Power_Supervisor:TPS3808DBV", "U", "TPS3808G01DBVR", {"VDD": "+3V3", "GND": "GND", "SENSE": "PF_SENSE", "~{RESET}": "PWR_FAIL_N"},
      "Package_TO_SOT_SMD:SOT-23-6", bosluk=1, dx=15)
R(gz, g, "240k 1%", "+12V_IN", "PF_SENSE"); R(gz, g, "10k 1%", "PF_SENSE", "GND"); C(gz, g, "1n", "PF_SENSE")
R(gz, g, "10k", "+3V3", "PWR_FAIL_N"); C(gz, g, "100n", "+3V3")
iki(gz, g, "Device:C_Polarized", "C", "470u 25V", "+12V_IN", "GND", "Capacitor_SMD:CP_Elec_8x10")
iki(gz, g, "Device:C_Polarized", "C", "470u 25V", "+12V_IN", "GND", "Capacitor_SMD:CP_Elec_8x10")

gz.metin("PELTIER SURUCUSU (DRV8837, 5 V, en cok 1 A): PWM_A isitir, PWM_B sogutur. Cikista bobin ve kondansator akimi duzlestirir", 30, 230)
gz.metin("(pusula ve IMU yakininda anahtarlama gurultusunu azaltir). Islemci sifirdayken girisler ic direncle sifirdadir: surucu kapali.", 30, 236)
g = Izgara(50, 280, sutun=12)
parca(gz, g, "Driver_Motor:DRV8837", "U", "DRV8837DSGR", {"VM": "+5V", "VCC": "+3V3", "GND": "GND", "~{SLEEP}": "+3V3",
      "IN1": "PELTIER_PWM_A", "IN2": "PELTIER_PWM_B", "OUT1": "TEC_SW_A", "OUT2": "TEC_SW_B"},
      "Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm", bosluk=1, dx=15)
iki(gz, g, "Device:L", "L", "10u 1,2A", "TEC_SW_A", "TEC_A", "Inductor_SMD:L_Taiyo-Yuden_NR-40xx")
iki(gz, g, "Device:L", "L", "10u 1,2A", "TEC_SW_B", "TEC_B", "Inductor_SMD:L_Taiyo-Yuden_NR-40xx")
C(gz, g, "10u 16V", "TEC_A", "TEC_B", fp=C0805); C(gz, g, "100n", "TEC_A"); C(gz, g, "100n", "TEC_B")
C(gz, g, "10u 16V", "+5V", fp=C0805); C(gz, g, "100n", "+3V3")
x, y = g.yer()
gz.koy(lib(gz, "Connector_Generic:Conn_01x02"), ref("J"), "Peltier", x + 5, y, {"Pin_1": "TEC_A", "Pin_2": "TEC_B"},
       footprint="Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal")
gz.yaz(os.path.join(BURASI, "gozetim.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_core.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, om, mcu, gc, ds, hb, sn, io, gz], {"operfly": "${KIPRJMOD}/../../ORTAK_KUTUPHANE/semboller/operfly.kicad_sym"})
print("elemanlar:", dict(sorted(sayac.items())))
