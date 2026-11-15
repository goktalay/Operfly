"""Operfly Power şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py POWER operfly_power`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_power", "2026-11-15")
kok = Sema(k.P, "Operfly Power", kagit="A3", tarih=k.T)
kok.metin("Operfly Power - guc karti (OPFPWR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/POWER/kicad/uret.py. Servo rayi henuz cizilmedi (README).", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA0": "VBAT_A_SENS", "PA1": "VBAT_B_SENS",          # ADC1_IN0, ADC1_IN1
      "PB10": "PWR_SCL", "PB11": "PWR_SDA",                # I2C2
      "PB3": "PWR_ALERT_N",
      "PA2": "V12_SENS"}                                   # ADC1_IN2: cevirici cikis gerilimi
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

# --- Cevirici: 6-60 V -> 12 V, 150 W, dort anahtarli dusuren-yukselten (LT8705A) ----
cv = Sema(k.P, "Operfly Power - 12 V cevirici (LT8705A, dort anahtarli dusuren-yukselten)", kagit="A1", tarih=k.T, ust=kok, ad="Cevirici", genel_etiket=True)
kok.alt_sayfa(cv, "cevirici.kicad_sch", 177.8, 50.8)
FET = "Package_TO_SOT_SMD:TDSON-8-1"
C1210 = "Capacitor_SMD:C_1210_3225Metric"
R2512 = "Resistor_SMD:R_2512_6332Metric"
cv.metin("12 V CEVIRICI: ureticinin '12 V cikis, 4-80 V giris' ornek devresi 5 A'den 12,5 A'e olceklendi (150 W).", 30, 28)
cv.metin("202 kHz, bobin 10 uH, akim direnci 4 mR, giris akim siniri 18 A (10 V altinda guc kendiliginden azalir).", 30, 34)
cv.metin("ILK TASLAK: kompanzasyon ve isil hesap benzetimle (LTspice) dogrulanmadan uretime gonderilmez.", 30, 40)
cv.koy(k.lib(cv, "Regulator_Switching:LT8705AxFE"), k.ref("U"), "LT8705AIFE", 130, 130, {
    "VIN": "VIN_SW", "CSPIN": "VIN", "CSNIN": "VIN_SW", "~{SHDN}": "CV_SHDN", "FBIN": "CV_FBIN", "MODE": "CV_LDO33", "SYNC": "GND",
    "RT": "CV_RT", "SS": "CV_SS", "INTVCC": "CV_INTVCC", "GATEVCC": "CV_INTVCC", "EXTVCC": "12V_OUT", "LDO33": "CV_LDO33",
    "TG1": "CV_TG1", "BOOST1": "CV_BOOST1", "SW1": "CV_SW1", "BG1": "CV_BG1", "CSP": "CV_CSP", "CSN": "CV_CSN",
    "BG2": "CV_BG2", "SW2": "CV_SW2", "BOOST2": "CV_BOOST2", "TG2": "CV_TG2",
    "CSPOUT": "12V_OUT", "CSNOUT": "12V_OUT", "IMON_OUT": "GND", "IMON_IN": "CV_IMON_IN", "FBOUT": "CV_FBOUT", "VC": "CV_VC", "GND": "GND",
}, footprint="Package_SO:Linear_HTSSOP-31-38-1EP_4.4x9.7mm_P0.5mm_EP2.74x4.75mm_ThermalVias")

cv.metin("AYAR ve DESTEK ELEMANLARI", 230, 60)
g = Izgara(240, 85, sutun=12)
k.R(cv, g, "215k 1%", "CV_RT", "GND")                                             # 202 kHz
k.R(cv, g, "71k5 1%", "VIN_SW", "CV_SHDN"); k.R(cv, g, "20k 1%", "CV_SHDN", "GND")  # 5,65 V'ta acar, 5,42 V'ta kapatir
k.R(cv, g, "100k 1%", "VIN_SW", "CV_FBIN"); k.R(cv, g, "26k1 1%", "CV_FBIN", "GND")  # giris 5,8 V'a duserse yuku azaltir
k.R(cv, g, "102k 1%", "12V_OUT", "CV_FBOUT"); k.R(cv, g, "11k3 1%", "CV_FBOUT", "GND")  # 12,1 V
k.R(cv, g, "33k2 1%", "CV_IMON_IN", "GND"); k.C(cv, g, "100n", "CV_IMON_IN")       # giris akim siniri 18 A
k.C(cv, g, "1u", "CV_SS", fp=C0603)
g.satir()
k.R(cv, g, "16k5", "CV_VC", "CV_VC_RC"); k.C(cv, g, "10n", "CV_VC_RC"); k.C(cv, g, "220p", "CV_VC")
k.C(cv, g, "4u7 16V", "CV_INTVCC", fp=C0805); k.C(cv, g, "4u7 16V", "CV_INTVCC", fp=C0805); k.C(cv, g, "100n", "CV_LDO33")
k.C(cv, g, "1u 100V", "VIN_SW", fp=C1206)
k.R(cv, g, "10R", "CV_RS", "CV_CSP"); k.C(cv, g, "1n", "CV_CSP"); k.R(cv, g, "10R", "GND", "CV_CSN"); k.C(cv, g, "1n", "CV_CSN")
g.satir()
k.iki(cv, g, "Device:D", "D", "ES1D (200 V, 1 A)", "CV_BOOST1", "CV_INTVCC", "Diode_SMD:D_SMA")
k.C(cv, g, "220n 25V", "CV_BOOST1", "CV_SW1", fp=C0603)
k.iki(cv, g, "Device:D", "D", "ES1D (200 V, 1 A)", "CV_BOOST2", "CV_INTVCC", "Diode_SMD:D_SMA")
k.C(cv, g, "220n 25V", "CV_BOOST2", "CV_SW2", fp=C0603)
k.R(cv, g, "2R", "CV_TG1", "CV_G1A"); k.R(cv, g, "2R", "CV_TG1", "CV_G1B")
k.bayrak(cv, g, "VIN_SW"); k.bayrak(cv, g, "12V_OUT")

cv.metin("GUC KATI: giris tarafi 100 V, 8 mR MOSFET (ikiser adet); cikis tarafi 40 V, 1,4 mR MOSFET (aday). Hepsi 6 V kapi geriliminde tam acilan tipte olmali.", 30, 250)
g = Izgara(50, 290, sutun=16, dx=26)
k.iki(cv, g, "Device:R", "R", "0R002 1% 3W", "VIN", "VIN_SW", R2512)                # giris akim olcumu
for _ in range(4):
    k.C(cv, g, "2u2 100V", "VIN_SW", fp=C1210)


def mosfet(deger, d, gate, src):
    x, y = g.yer()
    k.koy(cv, "Device:Q_NMOS", "Q", deger, x, y, {"D": d, "G": gate, "S": src}, FET)


M100 = "FDMS86101"
M40 = "BSC014N04LS"
mosfet(M100, "VIN_SW", "CV_G1A", "CV_SW1"); mosfet(M100, "VIN_SW", "CV_G1B", "CV_SW1")   # M1 x2: giris ust anahtar
mosfet(M100, "CV_SW1", "CV_BG1", "CV_RS"); mosfet(M100, "CV_SW1", "CV_BG1", "CV_RS")     # M2 x2: giris alt anahtar
k.iki(cv, g, "Device:L", "L", "10u XAL1510-103", "CV_SW1", "CV_SW2", "Inductor_SMD:L_Coilcraft_XAL1510-103")
mosfet(M40, "CV_SW2", "CV_BG2", "CV_RS")                                               # M3: cikis alt anahtar
mosfet(M40, "12V_OUT", "CV_TG2", "CV_SW2")                                             # M4: cikis ust anahtar
k.iki(cv, g, "Device:R", "R", "0R004 1% 3W", "CV_RS", "GND", R2512)                   # bobin akimi olcumu
g.satir()
for _ in range(4):
    k.C(cv, g, "22u 25V", "12V_OUT", fp=C1210)
k.iki(cv, g, "Device:C_Polarized", "C", "330u 25V", "12V_OUT", "GND", "Capacitor_SMD:CP_Elec_8x10")
k.iki(cv, g, "Device:C_Polarized", "C", "330u 25V", "12V_OUT", "GND", "Capacitor_SMD:CP_Elec_8x10")

cv.metin("CIKIS: 12 V ana cikis XT60 ile Hub'a gider (150 W omurga fisinden gecmez). Omurga fisi 2 A sigortayla beslenir; dugum buradan calisir.", 30, 370)
g = Izgara(50, 400, sutun=16, dx=26)
x, y = g.yer()
k.koy(cv, "Connector_Generic:Conn_01x02", "J", "12 V cikis (XT60)", x + 5, y, {"Pin_1": "12V_OUT", "Pin_2": "GND"}, "Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical")
k.iki(cv, g, "Device:Polyfuse", "F", "2 A (kendini onaran)", "12V_OUT", "+12V_BUS", "Fuse:Fuse_1812_4532Metric")
k.R(cv, g, "47k 1%", "12V_OUT", "V12_SENS"); k.R(cv, g, "10k 1%", "V12_SENS", "GND"); k.C(cv, g, "100n", "V12_SENS")
k.olcum_noktasi(cv, g, "12V_OUT")
cv.yaz(os.path.join(BURASI, "cevirici.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_power.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gr, cv], {"operfly": ORTAK_URI})
print("elemanlar:", dict(sorted(k.sayac.items())))
