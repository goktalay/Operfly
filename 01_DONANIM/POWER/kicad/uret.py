"""Operfly Power şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py POWER operfly_power`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_power", "2026-11-15")
kok = Sema(k.P, "Operfly Power", kagit="A3", tarih=k.T)
kok.metin("Operfly Power - guc karti (OPFPWR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/POWER/kicad/uret.py. 12 V cevirici ve servo rayi henuz cizilmedi (README).", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA0": "VBAT_A_SENS", "PA1": "VBAT_B_SENS",          # ADC1_IN0, ADC1_IN1
      "PB10": "PWR_SCL", "PB11": "PWR_SDA",                # I2C2
      "PB3": "PWR_ALERT_N"}
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

# --- Giris: iki batarya girisi, ideal diyotlar, giris olcumu -------------------
gr = Sema(k.P, "Operfly Power - batarya girisleri, ideal diyotlar, giris olcumu", kagit="A2", tarih=k.T, ust=kok, ad="Giris", genel_etiket=True)
kok.alt_sayfa(gr, "giris.kicad_sch", 101.6, 50.8)
gr.metin("BATARYA GIRISLERI (6-60 V): her giriste ideal diyot (LTC4359 + N kanal MOSFET). Devre ureticinin ornek devresidir:", 30, 30)
gr.metin("giriste iki kirpma diyotu (70 V ve ters yonde 24 V), VSS ucunda 1 k, cikista 47 nF. Ters baglanan batarya -40 V'a kadar zarar vermez.", 30, 36)
for i, h in enumerate("AB"):
    g = Izgara(50, 80 + i * 60, sutun=14)
    x, y = g.yer()
    k.koy(gr, "Connector_Generic:Conn_01x02", "J", "Batarya %s (XT60)" % h, x + 5, y, {"Pin_1": "BAT_%s" % h, "Pin_2": "GND"}, "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical")
    k.iki(gr, g, "Device:D_Zener", "D", "SMAT70A", "BAT_%s" % h, "TVS_%s" % h, "Diode_SMD:D_SMA")
    k.iki(gr, g, "Device:D_Zener", "D", "SMAJ24A", "GND", "TVS_%s" % h, "Diode_SMD:D_SMA")
    x, y = g.yer()
    k.koy(gr, "Device:Q_NMOS", "Q", "100V lojik seviye, <=4 mR (secilecek)", x, y, {"S": "BAT_%s" % h, "G": "GATE_%s" % h, "D": "VIN_OR"}, "Package_TO_SOT_SMD:TDSON-8-1")
    g.yer()
    k.parca(gr, g, "Power_Management:LTC4359-DCB", "U", "LTC4359IDCB", {"IN": "BAT_%s" % h, "SRC": "BAT_%s" % h, "GATE": "GATE_%s" % h, "OUT": "VIN_OR",
            "Vss": "VSS_%s" % h, "Pad": "VSS_%s" % h}, "Package_DFN_QFN:DFN-6-1EP_3x2mm_P0.5mm_EP1.65x1.35mm", dx=10)
    k.R(gr, g, "1k", "VSS_%s" % h, "GND"); k.C(gr, g, "47n 100V", "VIN_OR", fp=C0603)
    k.R(gr, g, "200k 1%", "BAT_%s" % h, "VBAT_%s_SENS" % h); k.R(gr, g, "10k 1%", "VBAT_%s_SENS" % h, "GND"); k.C(gr, g, "100n", "VBAT_%s_SENS" % h)
    k.bayrak(gr, g, "BAT_%s" % h); k.bayrak(gr, g, "VSS_%s" % h)

gr.metin("GIRIS OLCUMU (INA228): gerilim, akim ve harcanan enerji; I2C ile dugum islemcisine. Akim direnci 0,5 mR (30 A'de 0,45 W).", 30, 205)
gr.metin("VIN: olculmus, birlestirilmis giris gerilimi; 12 V ceviriciye ve servo rayina gider (bu sayfalar henuz cizilmedi).", 30, 211)
g = Izgara(50, 250, sutun=14)
x, y = g.yer()
k.koy(gr, "Device:R_Shunt", "R", "0R0005 1% 3W", x, y, {"1": "VIN_OR", "2": "SHUNT_P", "3": "SHUNT_N", "4": "VIN"}, "Resistor_SMD:R_Shunt_Isabellenhuette_BVR4026")
k.R(gr, g, "10R", "SHUNT_P", "INA_INP"); k.R(gr, g, "10R", "SHUNT_N", "INA_INN"); k.C(gr, g, "100n", "INA_INP", "INA_INN")
k.parca(gr, g, "Sensor_Energy:INA228", "U", "INA228AIDGSR", {"Vin+": "INA_INP", "Vin-": "INA_INN", "Vbus": "VIN", "VS": "+3V3", "GND": "GND",
        "A0": "GND", "A1": "GND", "SDA": "PWR_SDA", "SCL": "PWR_SCL", "~{Alert}": "PWR_ALERT_N"}, "Package_SO:TSSOP-10_3x3mm_P0.5mm", bosluk=2, dx=20)
k.C(gr, g, "100n", "+3V3"); k.R(gr, g, "2k2", "+3V3", "PWR_SCL"); k.R(gr, g, "2k2", "+3V3", "PWR_SDA"); k.R(gr, g, "10k", "+3V3", "PWR_ALERT_N")
g.satir()
k.iki(gr, g, "Device:C_Polarized", "C", "100u 80V", "VIN", "GND", "Capacitor_SMD:CP_Elec_10x10.5")
k.iki(gr, g, "Device:C_Polarized", "C", "100u 80V", "VIN", "GND", "Capacitor_SMD:CP_Elec_10x10.5")
k.C(gr, g, "2u2 100V", "VIN", fp="Capacitor_SMD:C_1210_3225Metric"); k.C(gr, g, "2u2 100V", "VIN", fp="Capacitor_SMD:C_1210_3225Metric")
k.olcum_noktasi(gr, g, "VIN")
gr.yaz(os.path.join(BURASI, "giris.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_power.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gr], {"operfly": ORTAK_URI})
print("elemanlar:", dict(sorted(k.sayac.items())))
