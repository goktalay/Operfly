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


def iki(sema, g, sembol, onek, deger, a, b, fp):
    """İki uçlu eleman: 1. uç a ağına, 2. uç b ağına."""
    x, y = g.yer()
    r = ref(onek)
    sema.koy(lib(sema, sembol), r, deger, x, y, {"1": a, "2": b}, footprint=fp)
    return r


def C(sema, g, deger, a, b="GND", fp=C0402):
    return iki(sema, g, "Device:C", "C", deger, a, b, fp)


def R(sema, g, deger, a, b, fp=R0402):
    return iki(sema, g, "Device:R", "R", deger, a, b, fp)


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
om.koy(bus, "J1", "Operfly Bus 1", 80, 90, port1)
om.koy(bus, "J2", "Operfly Bus 2 (yedek)", 190, 90, port2)
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

kok.yaz(os.path.join(BURASI, "operfly_core.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, om, mcu, gc, ds], {"operfly": "${KIPRJMOD}/../../ORTAK_KUTUPHANE/semboller/operfly.kicad_sym"})
print("elemanlar:", dict(sorted(sayac.items())))
