"""Operfly Range 10 / 30 / 100 şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py RANGE operfly_range`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Üç ürün tek karttır: düğüm devresi + hazır lazer mesafe modülü için arayüz (5 V anahtarlı besleme, 3,3 V seri port, I2C).
Menzili takılan modül belirler. Arayüz değerleri aday modüllerin veri sayfalarına göredir: besleme 5 V, haberleşme 3,3 V seviyeli
(Benewake TFmini Plus 12 m, TF02-Pro 40 m, TF03-100 100 m).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_range", "2026-11-15")
kok = Sema(k.P, "Operfly Range", kagit="A3", tarih=k.T)
kok.metin("Operfly Range 10 / 30 / 100 - mesafe sensoru karti (OPFR10, OPFR30, OPFR1H)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/RANGE/kicad/uret.py. Uc urun ayni karttir; menzili takilan modul belirler.", 25.4, 33.02, 1.6)

EK = {"PA2": "SENS_TX", "PA3": "SENS_RX",          # USART2: modulun seri portu (3,3 V)
      "PB10": "SENS_SCL_M", "PB11": "SENS_SDA_M",  # I2C2: I2C ile calisan moduller icin (ayni zamanda modulun G/C ucu)
      "PA4": "SENS_PWR_EN",                        # 1: module 5 V ver (sifirlamada kapali)
      "PA0": "SENS_VSENS"}                         # ADC1_IN0: modul besleme gerilimi / 2
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

sn = Sema(k.P, "Operfly Range - mesafe modulu arayuzu", kagit="A3", tarih=k.T, ust=kok, ad="Sensor", genel_etiket=True)
kok.alt_sayfa(sn, "sensor.kicad_sch", 101.6, 50.8)
sn.metin("MODUL KONNEKTORU (JST-GH 6, Operfly tanimi): 1 +5 V, 2 GND, 3 kart -> modul (modulun RX'i), 4 modul -> kart (modulun TX'i), 5 SCL / G-C, 6 SDA.", 20, 22)
sn.metin("Modulun kendi kablosu bu siraya gore hazirlanir. Hatlar 3,3 V seviyelidir; 470R seri direncler ve koruma diyotu kablo tarafindadir.", 20, 28)
g = Izgara(40, 70, sutun=11)
k.parca(sn, g, "Connector_Generic_MountingPin:Conn_01x06_MountingPin", "J", "Mesafe modulu", {"Pin_1": "+5V_SENS", "Pin_2": "GND", "Pin_3": "SENS_RXD", "Pin_4": "SENS_TXD",
        "Pin_5": "SENS_SCL", "Pin_6": "SENS_SDA", "MountPin": "GND"}, "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal", dx=8)
k.R(sn, g, "470R", "SENS_TX", "SENS_RXD"); k.R(sn, g, "470R", "SENS_TXD", "SENS_RX"); k.R(sn, g, "100k", "+3V3", "SENS_RX")
x, y = g.yer(); g.yer()
k.koy(sn, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "SENS_RXD", "6": "SENS_RXD", "3": "SENS_TXD", "4": "SENS_TXD", "5": "+3V3", "2": "GND"}, "Package_TO_SOT_SMD:SOT-666")
k.R(sn, g, "100R", "SENS_SCL_M", "SENS_SCL"); k.R(sn, g, "100R", "SENS_SDA_M", "SENS_SDA")
k.R(sn, g, "2k2", "+3V3", "SENS_SCL_M"); k.R(sn, g, "2k2", "+3V3", "SENS_SDA_M")

sn.metin("MODUL BESLEMESI: 5 V, P kanal MOSFET ile anahtarli (islemci modulu kapatip acabilir), 0,5 A tutma akimli kendini onaran sigorta.", 20, 125)
sn.metin("Aday moduller ortalama 0,11-0,2 A, tepe 0,3 A ceker. Kapi kondansatoru acilisi yumusatir. SENS_VSENS = besleme / 2.", 20, 131)
g = Izgara(40, 170, sutun=11)
x, y = g.yer()
k.koy(sn, "Transistor_FET:DMP3099L", "Q", "DMP3099L", x, y, {"S": "+5V", "D": "SENS_5V_SW", "G": "SENS_GATE"}, "Package_TO_SOT_SMD:SOT-23")
k.R(sn, g, "100k", "+5V", "SENS_GATE"); k.C(sn, g, "100n", "+5V", "SENS_GATE")
x, y = g.yer()
k.koy(sn, "Transistor_FET:2N7002", "Q", "2N7002", x, y, {"D": "SENS_GATE_R", "S": "GND", "G": "SENS_PWR_EN"}, "Package_TO_SOT_SMD:SOT-23")
k.R(sn, g, "10k", "SENS_GATE", "SENS_GATE_R"); k.R(sn, g, "100k", "SENS_PWR_EN", "GND")
k.iki(sn, g, "Device:Polyfuse", "F", "0,5 A tutma (1206)", "SENS_5V_SW", "+5V_SENS", "Fuse:Fuse_1206_3216Metric")
k.C(sn, g, "47u 10V", "+5V_SENS", fp=C1206); k.C(sn, g, "100n", "+5V_SENS")
k.R(sn, g, "10k 1%", "+5V_SENS", "SENS_VSENS"); k.R(sn, g, "10k 1%", "SENS_VSENS", "GND"); k.C(sn, g, "100n", "SENS_VSENS")
k.olcum_noktasi(sn, g, "+5V_SENS")
sn.yaz(os.path.join(BURASI, "sensor.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_range.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, sn], {"operfly": ORTAK_URI})
print("yazildi: operfly_range (kok + 2 sayfa)")
