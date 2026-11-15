"""Operfly Air şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py AIR operfly_air`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + fark basınç sensörü (pitot tüpü, hava hızı) + statik basınç sensörü + dış hava sıcaklığı girişi
+ pitot ısıtıcı çıkışı.
Devre değerleri üretici veri sayfalarındandır: MS5525DSO (TE, 11/2018), NCV8402 (onsemi).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_air", "2026-11-15")
kok = Sema(k.P, "Operfly Air", kagit="A3", tarih=k.T)
kok.metin("Operfly Air - hava hizi karti (OPFAIR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/AIR/kicad/uret.py.", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PB10": "SENS_SCL", "PB11": "SENS_SDA",      # I2C2: fark basinc (0x76) + statik basinc (0x77)
      "PB0": "BARO_INT",                           # statik basinc sensorunun veri hazir cikisi
      "PA0": "OAT_ADC",                            # ADC1_IN0: dis hava sicakligi (10 k NTC)
      "PA1": "HEAT_SENS",                          # ADC1_IN1: isitici donus hatti gerilimi x 0,18
      "PA2": "VBUS_SENS",                          # ADC1_IN2: omurga gerilimi x 0,18
      "PA8": "HEAT_EN"}                            # TIM1_CH1: pitot isiticisi (1 = acik; sifirlamada kapali)
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

sn = Sema(k.P, "Operfly Air - basinc sensorleri, sicaklik girisi, pitot isiticisi", kagit="A2", tarih=k.T, ust=kok, ad="Sensor", genel_etiket=True)
kok.alt_sayfa(sn, "sensor.kicad_sch", 101.6, 50.8)

sn.metin("FARK BASINC SENSORU (MS5525DSO-DB001DS: +-1 psi = +-6,9 kPa, 24 bit, I2C adres 0x76). Iki hortum ucu: Port 2 = pitot (toplam),", 30, 28)
sn.metin("Port 1 = statik. Olcum araligi deniz seviyesinde yaklasik 105 m/s'ye kadar. Ayni adli uclar ureticinin istedigi gibi kartta birlestirilir;", 30, 34)
sn.metin("SIN- ucu GND'ye BAGLANMAZ (uretici uyarisi). PS = 1: I2C. CSB = 1: adres 0x76.", 30, 40)
g = Izgara(50, 85, sutun=9)
k.parca(sn, g, "Sensor_Pressure:MS5525DSO", "U", "MS5525DSO-DB001DS", {
    "SUPPLY+": "+3V3", "SUPPLY-": "GND", "PS": "+3V3", "CSB": "+3V3", "SDI/SDA": "SENS_SDA", "SCLK/SCL": "SENS_SCL",
    "SIN-": "DP_SIN_N", "SOUT-": "DP_SOUT_N", "SOUT+": "DP_SOUT_P"}, "Sensor_Pressure:TE_MS5525DSO-DBxxxyS", bosluk=2, dx=22)
k.C(sn, g, "100n", "+3V3"); k.C(sn, g, "1u", "+3V3")
k.R(sn, g, "2k2", "+3V3", "SENS_SCL"); k.R(sn, g, "2k2", "+3V3", "SENS_SDA")

sn.metin("STATIK BASINC (BMP390, I2C adres 0x77): hava yogunlugu ve gercek hava hizi hesabi icin; kasa ici basinci olcer.", 30, 140)
g = Izgara(50, 180, sutun=9)
k.parca(sn, g, "operfly:BMP390", "U", "BMP390", {"SCK": "SENS_SCL", "SDI": "SENS_SDA", "SDO": "+3V3", "CSB": "+3V3", "INT": "BARO_INT",
        "VDD": "+3V3", "VDDIO": "+3V3", "VSS": "GND"}, "Package_LGA:ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y", bosluk=2, dx=20)
k.C(sn, g, "100n", "+3V3"); k.C(sn, g, "100n", "+3V3")

sn.metin("DIS HAVA SICAKLIGI: govde disina konan 10 k NTC (B = 3950) icin 2 uclu giris. 10 k %0,1 ile +3V3'e bolucu; olcum beslemeye oranlidir.", 30, 230)
g = Izgara(50, 270, sutun=9)
k.parca(sn, g, "Connector_Generic_MountingPin:Conn_01x02_MountingPin", "J", "Dis sicaklik (NTC)", {"Pin_1": "OAT_NTC", "Pin_2": "GND", "MountPin": "GND"},
        "Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal", dx=8)
k.R(sn, g, "10k 0.1%", "+3V3", "OAT_NTC"); k.R(sn, g, "1k", "OAT_NTC", "OAT_ADC"); k.C(sn, g, "100n", "OAT_ADC")

sn.metin("PITOT ISITICISI (12 V, en cok 1 A = 12 W): korumali alt taraf anahtari NCV8402 (akim siniri ~4 A, asiri sicaklikta kapanir, 42 V kirpma).", 270, 28)
sn.metin("Kapisi 5 V ister; islemcinin 3,3 V cikisi 74AHCT1G125 ile 5 V'a cevrilir. Sifirlamada ve 5 V yokken isitici KAPALIDIR.", 270, 34)
sn.metin("HEAT_SENS: kapaliyken ~2,2 V = isitici bagli, 0 V = isitici yok/kopuk; acikken 0,1 V alti = normal, yuksek = koruma devrede.", 270, 40)
sn.metin("Arti hat 1,5 A tutma akimli kendini onaran sigortadan gecer (kablonun govdeye kisa devresi icin).", 270, 46)
g = Izgara(290, 90, sutun=9)
k.parca(sn, g, "Connector_Generic:Conn_01x02", "J", "Pitot isiticisi (Micro-Fit)", {"Pin_1": "+12V_HEAT", "Pin_2": "HEAT_RET"},
        "Connector_Molex:Molex_Micro-Fit_3.0_43650-0200_1x02_P3.00mm_Horizontal", dx=8)
k.iki(sn, g, "Device:Polyfuse", "F", "1,5 A tutma, 30 V (1812)", "+12V", "+12V_HEAT", "Fuse:Fuse_1812_4532Metric")
k.C(sn, g, "100n 50V", "+12V_HEAT", fp=C0603)
x, y = g.yer(); g.yer()
k.koy(sn, "Transistor_FET_Other:NCV8402xST", "Q", "NCV8402STT1G", x + 8, y, {"D": "HEAT_RET", "S": "GND", "G": "HEAT_G"}, "Package_TO_SOT_SMD:SOT-223")
g.satir()
x, y = g.yer(); g.yer()
k.koy(sn, "74xGxx:74AHCT1G125", "U", "74AHCT1G125", x + 10, y, {"1": "GND", "2": "HEAT_EN", "4": "HEAT_DRV", "5": "+5V", "3": "GND"}, "Package_TO_SOT_SMD:SOT-353_SC-70-5")
k.C(sn, g, "100n", "+5V"); k.R(sn, g, "100k", "HEAT_EN", "GND"); k.R(sn, g, "1k", "HEAT_DRV", "HEAT_G"); k.R(sn, g, "100k", "HEAT_G", "GND")
g.satir()
k.R(sn, g, "100k 1%", "HEAT_RET", "HEAT_SENS"); k.R(sn, g, "22k 1%", "HEAT_SENS", "GND"); k.C(sn, g, "100n", "HEAT_SENS")
k.R(sn, g, "100k 1%", "+12V", "VBUS_SENS"); k.R(sn, g, "22k 1%", "VBUS_SENS", "GND"); k.C(sn, g, "100n", "VBUS_SENS")
k.olcum_noktasi(sn, g, "HEAT_RET")
sn.yaz(os.path.join(BURASI, "sensor.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_air.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, sn], {"operfly": ORTAK_URI})
print("yazildi: operfly_air (kok + 2 sayfa)")
