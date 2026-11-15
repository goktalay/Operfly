"""Operfly Engine şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py ENGINE operfly_engine`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + yalıtımlı motor ölçüm adası (iki termokupl, iki NTC, yakıt seviyesi, yakıt akışı)
+ yalıtımlı devir girişi + ateşleme besleme anahtarı (motor durdurma).
Üç ayrı toprak vardır: GND (omurga), GND_ISO (ölçüm adası), IGN_GND (ateşleme beslemesi). Aralarında yalnızca yalıtıcılar bulunur
(IGN_GND ile GND_ISO arasında ateşleme gerilimi ölçümü için 1 k).
Devre değerleri üretici veri sayfalarındandır: ISO7762 (TI SLLSEU1), NXE1 (Murata KDC_NXE1), MCP3208 (Microchip DS21298E),
AD849x (Analog Devices), LTV-817 (Lite-On), DMP3099L (Diodes), LM4040 (TI).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_engine", "2026-11-15")
kok = Sema(k.P, "Operfly Engine", kagit="A3", tarih=k.T)
kok.metin("Operfly Engine - benzinli motor izleme ve durdurma karti (OPFENG)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/ENGINE/kicad/uret.py.", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA5": "ISO_SCK", "PA7": "ISO_MOSI", "PA6": "ISO_MISO", "PA4": "ISO_CS",   # SPI1: yalitimli adadaki ADC
      "PA0": "TACH_IN",                            # TIM2_CH1: devir darbesi (0 = darbe)
      "PA1": "FLOW_IN",                            # TIM2_CH2: yakit akis olcer darbesi
      "PB0": "KILL_A", "PB1": "KILL_B",            # motor durdurma: yalnizca KILL_A = 1 VE KILL_B = 0 iken keser
      "PB3": "IGN_FB"}                             # 0 = atesleme cikisinda gerilim var
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)
OPTO = ("Isolator:LTV-817S", "U", "LTV-817S", "Package_DIP:SMDIP-4_W9.53mm")
GH = "Connector_JST:JST_GH_SM%02dB-GHS-TB_1x%02d-1MP_P1.25mm_Horizontal"


def gh(sema, g, n, ad, uclar):
    ag = {"Pin_%d" % (i + 1): a for i, a in enumerate(uclar)}
    ag["MountPin"] = "GND_ISO"
    return k.parca(sema, g, "Connector_Generic_MountingPin:Conn_01x%02d_MountingPin" % n, "J", ad, ag, GH % (n, n), dx=8)


# --- Ölçüm adası ---------------------------------------------------------------
ol = Sema(k.P, "Operfly Engine - yalitimli olcum adasi: besleme, ADC, sicakliklar, yakit", kagit="A1", tarih=k.T, ust=kok, ad="Olcum", genel_etiket=True)
kok.alt_sayfa(ol, "olcum.kicad_sch", 101.6, 50.8)

ol.metin("YALITIMLI BESLEME (NXE1S0505MC: 5 V -> 5 V, 1 W, 3 kV): ada gerilimi yuke gore 4,5-5,5 V arasinda degisir (duzenlemesiz modul).", 30, 28)
ol.metin("220R on yuk modulun en az yuk sartini (%10) saglar. Olcumler 4,096 V referansa gore yapildigi icin ada gerilimindeki degisim sonucu etkilemez.", 30, 34)
g = Izgara(50, 75, sutun=12)
k.iki(ol, g, "Device:FerriteBead", "FB", "BLM18PG221", "+5V", "+5V_DCDC", "Inductor_SMD:L_0603_1608Metric")
k.C(ol, g, "4u7 16V", "+5V_DCDC", fp=C0805)
k.parca(ol, g, "Converter_DCDC_Isolated:NXE1S0505MC", "U", "NXE1S0505MC", {"+VIN": "+5V_DCDC", "-VIN": "GND", "+VOUT": "+5V_ISO", "-VOUT": "GND_ISO"},
        "Converter_DCDC:Converter_DCDC_Murata_NXExSxxxxMC_SMD", bosluk=2, dx=18)
k.C(ol, g, "4u7 16V", "+5V_ISO", "GND_ISO", fp=C0805); k.C(ol, g, "100n", "+5V_ISO", "GND_ISO")
k.R(ol, g, "220R", "+5V_ISO", "GND_ISO", fp="Resistor_SMD:R_0805_2012Metric")
k.bayrak(ol, g, "+5V_DCDC")
k.olcum_noktasi(ol, g, "+5V_ISO"); k.olcum_noktasi(ol, g, "GND_ISO")

ol.metin("SPI YALITICI (ISO7762: 4 ileri + 2 geri kanal; iki tarafi ayri beslenir: islemci tarafi 3,3 V, ada tarafi 5 V).", 30, 120)
ol.metin("A: saat, B: veri (islemci -> ADC), C: secme, D: bos; E: veri (ADC -> islemci), F: yakit akis darbesi.", 30, 126)
g = Izgara(50, 170, sutun=12)
k.parca(ol, g, "Isolator:ISO7762DW", "U", "ISO7762DW", {
    "Vcc1": "+3V3", "GND1": "GND", "Vcc2": "+5V_ISO", "GND2": "GND_ISO",
    "INA": "ISO_SCK", "INB": "ISO_MOSI", "INC": "ISO_CS", "IND": "GND", "OUTE": "ISO_MISO", "OUTF": "FLOW_IN",
    "OUTA": "ADC_CLK", "OUTB": "ADC_DIN", "OUTC": "ADC_CS", "INE": "ADC_DOUT", "INF": "FLOW_F"}, "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm", bosluk=2, dx=18)
k.C(ol, g, "100n", "+3V3"); k.C(ol, g, "100n", "+5V_ISO", "GND_ISO")

ol.metin("ADC (MCP3208, 12 bit, 8 kanal) ve REFERANS (LM4040 4,096 V): 1 basamak = 1 mV. Kanallar: 0-1 termokupl, 2-3 NTC, 4 yakit seviyesi,", 30, 215)
ol.metin("5 atesleme gerilimi, 6 ada gerilimi / 2, 7 bos (GND_ISO). SPI saati en cok 2 MHz.", 30, 221)
g = Izgara(50, 265, sutun=12)
k.parca(ol, g, "Analog_ADC:MCP3208", "U", "MCP3208-CI/SL", {
    "Vdd": "+5V_ISO", "Vref": "VREF_ISO", "AGND": "GND_ISO", "DGND": "GND_ISO", "CLK": "ADC_CLK", "Din": "ADC_DIN", "Dout": "ADC_DOUT", "~{CS}/SHDN": "ADC_CS",
    "CH0": "ADC_TC1", "CH1": "ADC_TC2", "CH2": "ADC_NTC1", "CH3": "ADC_NTC2", "CH4": "ADC_FUEL", "CH5": "ADC_IGN", "CH6": "ADC_VISO", "CH7": "GND_ISO"},
    "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", bosluk=2, dx=22)
k.C(ol, g, "100n", "+5V_ISO", "GND_ISO"); k.C(ol, g, "1u", "+5V_ISO", "GND_ISO")
k.R(ol, g, "150R", "+5V_ISO", "VREF_ISO")
x, y = g.yer()
k.koy(ol, "Reference_Voltage:LM4040DBZ-4.1", "U", "LM4040AIM3-4.1", x, y, {"K": "VREF_ISO", "A": "GND_ISO"}, "Package_TO_SOT_SMD:SOT-23")
k.C(ol, g, "1u", "VREF_ISO", "GND_ISO"); k.bayrak(ol, g, "VREF_ISO")
k.R(ol, g, "10k 1%", "+5V_ISO", "ADC_VISO"); k.R(ol, g, "10k 1%", "ADC_VISO", "GND_ISO"); k.C(ol, g, "100n", "ADC_VISO", "GND_ISO")

ol.metin("TERMOKUPL GIRISLERI (K tipi; AD8495: soguk uc duzeltmeli, 5 mV/C): 1 = silindir kafasi, 2 = egzoz. Olcum ust siniri 4,096 V = yaklasik 800 C.", 330, 28)
ol.metin("Eksi uc 1M ile GND_ISO'ya bagli (uretici onerisi): govdeye degen termokuplla da calisir, kopuk termokuplda cikis tavana gider.", 330, 34)
ol.metin("Giris suzgeci: 4k7 + 10n (ortak) + 1u (fark). Termokupl klemensi entegrenin HEMEN yaninda olmali (soguk uc sicakligi ayni olsun).", 330, 40)
g = Izgara(350, 80, sutun=13)
for i in (1, 2):
    k.parca(ol, g, "Connector_Generic:Conn_01x02", "J", "Termokupl %d (K)" % i, {"Pin_1": "TC%d_P" % i, "Pin_2": "TC%d_N" % i},
            "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-2-2.54_1x02_P2.54mm_Horizontal", dx=8)
    k.R(ol, g, "4k7 1%", "TC%d_P" % i, "TC%d_PF" % i); k.R(ol, g, "4k7 1%", "TC%d_N" % i, "TC%d_NF" % i)
    k.C(ol, g, "10n", "TC%d_PF" % i, "GND_ISO"); k.C(ol, g, "10n", "TC%d_NF" % i, "GND_ISO"); k.C(ol, g, "1u", "TC%d_PF" % i, "TC%d_NF" % i, fp=C0603)
    k.R(ol, g, "1M", "TC%d_NF" % i, "GND_ISO")
    x, y = g.yer(); g.yer()
    k.koy(ol, "Sensor_Temperature:AD8495", "U", "AD8495ARMZ", x + 10, y, {"+IN": "TC%d_PF" % i, "-IN": "TC%d_NF" % i, "REF": "GND_ISO", "-Vs": "GND_ISO",
          "+Vs": "+5V_ISO", "SENSE": "TC%d_OUT" % i, "6": "TC%d_OUT" % i}, "Package_SO:MSOP-8_3x3mm_P0.65mm")
    k.C(ol, g, "100n", "+5V_ISO", "GND_ISO"); k.R(ol, g, "1k", "TC%d_OUT" % i, "ADC_TC%d" % i); k.C(ol, g, "100n", "ADC_TC%d" % i, "GND_ISO")
    g.satir()

ol.metin("NTC GIRISLERI (2 adet, 10 k): 10 k %0,1 ile referansa bolucu (olcum referansa oranli). Ornek: yag/sogutma, karbrator havasi.", 330, 170)
g = Izgara(350, 210, sutun=13)
gh(ol, g, 4, "NTC 1-2", ["NTC1", "GND_ISO", "NTC2", "GND_ISO"])
for i in (1, 2):
    k.R(ol, g, "10k 0.1%", "VREF_ISO", "NTC%d" % i); k.R(ol, g, "1k", "NTC%d" % i, "ADC_NTC%d" % i); k.C(ol, g, "100n", "ADC_NTC%d" % i, "GND_ISO")

ol.metin("YAKIT: seviye (0-5 V analog; 10k/39k ile 0-3,98 V) ve akis olcer darbesi (acik kollektor; 10k yukari cekme). Sensor beslemesi +5V_SENS", 330, 260)
ol.metin("0,1 A'lik kendini onaran sigortadan gecer: dis kablodaki kisa devre adayi cokertmez.", 330, 266)
g = Izgara(350, 305, sutun=13)
gh(ol, g, 4, "Yakit", ["+5V_SENS", "FUEL_LVL", "FLOW", "GND_ISO"])
k.iki(ol, g, "Device:Polyfuse", "F", "0,1 A tutma (1206)", "+5V_ISO", "+5V_SENS", "Fuse:Fuse_1206_3216Metric")
k.C(ol, g, "100n", "+5V_SENS", "GND_ISO")
k.R(ol, g, "10k 1%", "FUEL_LVL", "ADC_FUEL"); k.R(ol, g, "39k 1%", "ADC_FUEL", "GND_ISO"); k.C(ol, g, "100n", "ADC_FUEL", "GND_ISO")
k.R(ol, g, "10k", "+5V_ISO", "FLOW"); k.R(ol, g, "1k", "FLOW", "FLOW_F"); k.C(ol, g, "1n", "FLOW_F", "GND_ISO")
ol.yaz(os.path.join(BURASI, "olcum.kicad_sch"))

# --- Devir girişi ve ateşleme anahtarı ---------------------------------------------
at = Sema(k.P, "Operfly Engine - devir girisi, atesleme anahtari (motor durdurma)", kagit="A2", tarih=k.T, ust=kok, ad="Atesleme", genel_etiket=True)
kok.alt_sayfa(at, "atesleme.kicad_sch", 177.8, 50.8)

at.metin("DEVIR GIRISI (optokuplorle yalitimli, iki uclu): TACH+ ile TACH- arasina 3-15 V darbe. Acik kollektorlu sensorde (Hall):", 30, 28)
at.metin("TACH+ = +5V_SENS, TACH- = sensor cikisi. Gerilim darbesi veren atesleme modulunde: TACH+ = darbe, TACH- = modulun topragi.", 30, 34)
g = Izgara(50, 75, sutun=9)
gh(at, g, 4, "Devir", ["+5V_SENS", "TACH_P", "TACH_N", "GND_ISO"])
k.R(at, g, "680R", "TACH_P", "TACH_A", fp="Resistor_SMD:R_0603_1608Metric")
k.iki(at, g, "Diode:1N4148W", "D", "1N4148W", "TACH_A", "TACH_N", "Diode_SMD:D_SOD-123")
x, y = g.yer(); g.yer()
k.koy(at, OPTO[0], OPTO[1], OPTO[2], x + 10, y, {"1": "TACH_A", "2": "TACH_N", "4": "TACH_IN", "3": "GND"}, OPTO[3])
k.R(at, g, "4k7", "+3V3", "TACH_IN"); k.C(at, g, "1n", "TACH_IN")

at.metin("ATESLEME BESLEME ANAHTARI: atesleme bataryasi (4,8-14 V) IGN_IN'den girer, atesleme modulune IGN_OUT'tan cikar. En cok 2 A surekli.", 30, 130)
at.metin("Anahtar KENDILIGINDEN ACIKTIR: kart beslemesiz ya da arizali olsa da motor calisir. Durdurmak icin islemci optokuplorun isigini", 30, 136)
at.metin("yakar (KILL_A = 1 VE KILL_B = 0); optokuplor kapiyi kaynaga baglar, transistorler kapanir. Iki ayri islemci ucu: tek uc arizasi motoru durdurmaz.", 30, 142)
at.metin("Harici durdurma girisi: iki ucu kisa devre edilirse motor islemciden bagimsiz durur (yer guvenligi anahtari). Uclardan biri 470R ile", 30, 148)
at.metin("bataryaya, digeri kapiya gider: kablonun govdeye degmesi bataryayi kisa devre etmez.", 30, 154)
g = Izgara(50, 190, sutun=9)
k.parca(at, g, "Connector_Generic:Conn_01x04", "J", "Atesleme (Micro-Fit)", {"Pin_1": "IGN_IN", "Pin_2": "IGN_GND", "Pin_3": "IGN_OUT", "Pin_4": "IGN_GND"},
        "Connector_Molex:Molex_Micro-Fit_3.0_43650-0400_1x04_P3.00mm_Horizontal", dx=8)
k.iki(at, g, "Device:D_TVS", "D", "SMBJ16A", "IGN_IN", "IGN_GND", "Diode_SMD:D_SMB")
k.C(at, g, "1u 50V", "IGN_IN", "IGN_GND", fp=C0805)
for _ in range(2):
    x, y = g.yer()
    k.koy(at, "Transistor_FET:DMP3099L", "Q", "DMP3099L", x, y, {"S": "IGN_IN", "D": "IGN_OUT", "G": "IGN_GATE"}, "Package_TO_SOT_SMD:SOT-23")
k.R(at, g, "22k", "IGN_GATE", "IGN_GND"); k.C(at, g, "100n 50V", "IGN_IN", "IGN_GATE", fp=C0603)
k.iki(at, g, "Diode:BZT52Bxx", "D", "BZT52B10 (10 V)", "IGN_IN", "IGN_GATE", "Diode_SMD:D_SOD-123F")
g.satir()
x, y = g.yer(); g.yer()
k.koy(at, OPTO[0], OPTO[1], OPTO[2], x + 10, y, {"1": "KILL_LED", "2": "KILL_B", "4": "IGN_IN", "3": "IGN_GATE"}, OPTO[3])
k.R(at, g, "220R", "KILL_A", "KILL_LED"); k.R(at, g, "100k", "KILL_A", "GND"); k.R(at, g, "100k", "+3V3", "KILL_B")
k.parca(at, g, "Connector_Generic_MountingPin:Conn_01x02_MountingPin", "J", "Harici durdurma", {"Pin_1": "KILL_EXT", "Pin_2": "IGN_GATE", "MountPin": "IGN_GND"},
        GH % (2, 2), dx=8)
k.R(at, g, "470R", "IGN_IN", "KILL_EXT")
k.olcum_noktasi(at, g, "IGN_GATE")

at.metin("ATESLEME GERI BILDIRIMI ve GERILIM OLCUMU: IGN_FB = 0 atesleme cikisinda gerilim var demektir (islemci kesmenin gerceklestigini gorur).", 30, 290)
at.metin("Atesleme gerilimi ADC'nin 5. kanalinda (x 0,18). IGN_GND ile GND_ISO yalnizca 1 k uzerinden baglidir (olcum icin ortak nokta).", 30, 296)
g = Izgara(50, 335, sutun=9)
k.R(at, g, "2k2", "IGN_OUT", "IGN_FB_A", fp="Resistor_SMD:R_0603_1608Metric")
k.iki(at, g, "Diode:1N4148W", "D", "1N4148W", "IGN_FB_A", "IGN_GND", "Diode_SMD:D_SOD-123")
x, y = g.yer(); g.yer()
k.koy(at, OPTO[0], OPTO[1], OPTO[2], x + 10, y, {"1": "IGN_FB_A", "2": "IGN_GND", "4": "IGN_FB", "3": "GND"}, OPTO[3])
k.R(at, g, "10k", "+3V3", "IGN_FB")
k.R(at, g, "100k 1%", "IGN_OUT", "ADC_IGN"); k.R(at, g, "22k 1%", "ADC_IGN", "GND_ISO"); k.C(at, g, "100n", "ADC_IGN", "GND_ISO")
k.R(at, g, "1k", "IGN_GND", "GND_ISO", fp="Resistor_SMD:R_0805_2012Metric")
at.yaz(os.path.join(BURASI, "atesleme.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_engine.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, ol, at], {"operfly": ORTAK_URI})
print("yazildi: operfly_engine (kok + 3 sayfa)")
