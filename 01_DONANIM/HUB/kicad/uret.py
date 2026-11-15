"""Operfly Hub şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py HUB operfly_hub`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Bu sürümde güç dağıtımı çizilidir (12 port, port başına elektronik sigorta ve akım ölçümü). Ethernet anahtarı
ayrı sayfadır ve henüz çizilmemiştir; portların Ethernet uçları şimdilik bağlı değildir.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
PORT = 12
k = Kart("operfly_hub", "2026-11-15")
kok = Sema(k.P, "Operfly Hub", kagit="A3", tarih=k.T)
kok.metin("Operfly Hub - omurga merkezi (OPFHUB)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/HUB/kicad/uret.py. Ethernet anahtari sayfasi henuz cizilmedi (README).", 25.4, 33.02, 1.6)

EK = {"PA0": "IMON_MUX", "PA1": "V12_SENS",                               # ADC1_IN0, ADC1_IN1
      "PA4": "MUX_S0", "PA5": "MUX_S1", "PA6": "MUX_S2", "PA7": "MUX_S3",
      "PB10": "HUB_SCL", "PB11": "HUB_SDA", "PB3": "EXP_INT_N"}           # I2C2
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, port=False, sonlandirma=True)

# --- Guc girisi ve ortak denetim ----------------------------------------------
gc = Sema(k.P, "Operfly Hub - guc girisi, port denetimi ve akim olcumu", kagit="A1", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gc, "guc.kicad_sch", 101.6, 50.8)
gc.metin("12 V GIRIS (Power kartindan, XT60). Dugum devresi 2 A sigortayla ayni hattan beslenir.", 30, 30)
g = Izgara(50, 65, sutun=14)
x, y = g.yer()
k.koy(gc, "Connector_Generic:Conn_01x02", "J", "12 V giris (XT60)", x + 5, y, {"Pin_1": "+12V_HUB", "Pin_2": "GND"}, "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical")
k.iki(gc, g, "Device:D_TVS", "D", "SMBJ18A", "+12V_HUB", "GND", "Diode_SMD:D_SMB")
k.iki(gc, g, "Device:C_Polarized", "C", "330u 25V", "+12V_HUB", "GND", "Capacitor_SMD:CP_Elec_8x10")
k.iki(gc, g, "Device:C_Polarized", "C", "330u 25V", "+12V_HUB", "GND", "Capacitor_SMD:CP_Elec_8x10")
k.iki(gc, g, "Device:Polyfuse", "F", "2 A (kendini onaran)", "+12V_HUB", "+12V_BUS", "Fuse:Fuse_1812_4532Metric")
k.R(gc, g, "47k 1%", "+12V_HUB", "V12_SENS"); k.R(gc, g, "10k 1%", "V12_SENS", "GND"); k.C(gc, g, "100n", "V12_SENS")
k.bayrak(gc, g, "+12V_HUB")

gc.metin("ORTAK ESIKLER: portlar giris 9,6 V'u gecince acilir (9,0 V altinda kapanir); 15 V ustunde kapanir.", 30, 115)
g = Izgara(50, 145, sutun=14)
k.R(gc, g, "100k 1%", "+12V_HUB", "HUB_UVLO"); k.R(gc, g, "14k3 1%", "HUB_UVLO", "GND")
k.R(gc, g, "100k 1%", "+12V_HUB", "HUB_OVP"); k.R(gc, g, "8k66 1%", "HUB_OVP", "GND")

gc.metin("PORT DENETIMI: 1. genisletici portlari acar/kapatir (adres 0x20), 2. genisletici ariza girislerini okur (adres 0x21).", 30, 195)
gc.metin("AKIM OLCUMU: 12 portun akim cikisi tek bir analog seciciyle isleme alinir (6 A = 3,0 V).", 30, 201)
en = {"IO%d_%d" % (n // 8, n % 8): "P%d_EN" % (n + 1) for n in range(PORT)}
fl = {"IO%d_%d" % (n // 8, n % 8): "P%d_FLT_N" % (n + 1) for n in range(PORT)}
ortak = {"VDD": "+3V3", "VSS": "GND", "SCL": "HUB_SCL", "SDA": "HUB_SDA", "A1": "GND", "A2": "GND"}
k.koy(gc, "Interface_Expansion:PCA9555PW", "U", "PCA9555PW", 90, 270, dict(en, A0="GND", **ortak), "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm")
k.koy(gc, "Interface_Expansion:PCA9555PW", "U", "PCA9555PW", 220, 270, dict(fl, A0="+3V3", **{"~{INT}": "EXP_INT_N"}, **ortak), "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm")
mux = {"I%d" % n: ("P%d_IMON" % (n + 1) if n < PORT else "GND") for n in range(16)}
mux.update({"COM": "IMON_MUX", "S0": "MUX_S0", "S1": "MUX_S1", "S2": "MUX_S2", "S3": "MUX_S3", "~{E}": "GND", "VCC": "+3V3", "GND": "GND"})
k.koy(gc, "74xx:CD74HC4067SM", "U", "CD74HC4067SM96", 360, 270, mux, "Package_SO:SSOP-24_5.3x8.2mm_P0.65mm")
g = Izgara(440, 240, sutun=8)
k.R(gc, g, "2k2", "+3V3", "HUB_SCL"); k.R(gc, g, "2k2", "+3V3", "HUB_SDA"); k.R(gc, g, "10k", "+3V3", "EXP_INT_N")
for _ in range(3):
    k.C(gc, g, "100n", "+3V3")
k.C(gc, g, "100n", "IMON_MUX")
gc.yaz(os.path.join(BURASI, "guc.kicad_sch"))

# --- Portlar: 12 omurga portu, her birinde elektronik sigorta -----------------
pt = Sema(k.P, "Operfly Hub - 12 omurga portu ve port sigortalari", kagit="A0", tarih=k.T, ust=kok, ad="Portlar", genel_etiket=True)
kok.alt_sayfa(pt, "portlar.kicad_sch", 177.8, 50.8)
pt.metin("Her portta TPS26630: akim siniri 6 A (3k01), yumusak acilis ~11 ms (47 nF), asiri akimda kendiliginden yeniden dener.", 30, 25)
pt.metin("CAN A/B ve PPS tum portlarda ortaktir. Ethernet uclari anahtar sayfasi cizilene kadar bagli degildir.", 30, 31)
for n in range(1, PORT + 1):
    x0, y0 = 30 + ((n - 1) % 4) * 285, 50 + ((n - 1) // 4) * 255
    p = "P%d" % n
    pt.metin("PORT %d" % n, x0, y0, 2.5)
    k.koy(pt, "operfly:Operfly_Bus_20", "J", "Port %d" % n, x0 + 35, y0 + 60, {"+12V": p + "_12V", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L",
          "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L", "PPS": "PPS_BUS"}, "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical")
    k.koy(pt, "Power_Management:TPS26630RGE", "U", "TPS26630RGER", x0 + 120, y0 + 60, {
        "IN": "+12V_HUB", "IN_SYS": "+12V_HUB", "UVLO": "HUB_UVLO", "OVP": "HUB_OVP", "GND": "GND", "MODE": "GND",
        "dVdT": p + "_DVDT", "ILIM": p + "_ILIM", "~{SHDN}": p + "_EN", "IMON": p + "_IMON", "~{FLT}": p + "_FLT_N",
        "PGTH": p + "_PGTH", "OUT": p + "_12V"}, "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias")
    g = Izgara(x0 + 20, y0 + 135, sutun=10, dx=24)
    k.C(pt, g, "100n 50V", "+12V_HUB", fp=C0603); k.C(pt, g, "1u 25V", p + "_12V", fp=C0603)
    k.R(pt, g, "3k01 1%", p + "_ILIM", "GND"); k.C(pt, g, "47n", p + "_DVDT")
    k.R(pt, g, "18k 1%", p + "_IMON", "GND"); k.C(pt, g, "100n", p + "_IMON")
    k.R(pt, g, "100k", "+3V3", p + "_EN"); k.R(pt, g, "10k", "+3V3", p + "_FLT_N")
    k.R(pt, g, "100k 1%", p + "_12V", p + "_PGTH"); k.R(pt, g, "13k7 1%", p + "_PGTH", "GND")
pt.yaz(os.path.join(BURASI, "portlar.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_hub.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gc, pt], {"operfly": ORTAK_URI})
print("elemanlar:", dict(sorted(k.sayac.items())))
