"""Operfly RX şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py RX operfly_rx`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + kumanda radyo modülü (RFDesign RFD900ux-SMT; 868 MHz sürümü RFD868ux-SMT aynı ayak izine oturur),
modüle ayrı 5,3 V besleme, iki anten konnektörü.
Modülün uç sırası ve kart önerileri üreticinin veri sayfasındandır (RFD900ux/RFD868ux Data Sheet V1.3).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
k = Kart("operfly_rx", "2026-11-15")
kok = Sema(k.P, "Operfly RX", kagit="A3", tarih=k.T)
kok.metin("Operfly RX - arac tarafi kumanda alicisi (OPFRCV)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/RX/kicad/uret.py.", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA2": "RADIO_RXD", "PA3": "RADIO_TXD",              # USART2_TX -> modul RX, USART2_RX <- modul TX
      "PA1": "RADIO_CTS", "PA0": "RADIO_RTS",              # USART2_RTS -> modul CTS, USART2_CTS <- modul RTS
      "PA4": "RADIO_OFF",                                  # 1: modul beslemesi kapali (sifirlamada acik)
      "PB0": "RADIO_BOOT_N",                               # 0 iken besleme acilirsa modul yazilim yukleme kipine girer
      "PA5": "RADIO_VSENS",                                # ADC1_IN5: modul besleme gerilimi / 2
      "PB3": "RADIO_GPIO0", "PB4": "RADIO_GPIO1"}          # modulun iki genel amacli ucu (GPIO1 darbe girisi/cikisi olabilir)
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

rd = Sema(k.P, "Operfly RX - kumanda radyo modulu, besleme, antenler", kagit="A2", tarih=k.T, ust=kok, ad="Radyo", genel_etiket=True)
kok.alt_sayfa(rd, "radyo.kicad_sch", 101.6, 50.8)
rd.metin("KUMANDA RADYO MODULU (RFDesign RFD900ux-SMT; 868 MHz icin RFD868ux-SMT ayni yere oturur). Uc sirasi uretici veri sayfasindan.", 30, 28)
rd.metin("Seri arayuz 3,3 V (en cok 3,5 V). USB uclari uretici tarafindan devre disi, bos. +3V3_OUT modulun kendi regulator cikisi, yuklenmez.", 30, 34)
rd.metin("Islemciden module giden hatlarda 470R: modul beslemesi kapaliyken girislerinden akim akmasini sinirlar.", 30, 40)
k.koy(rd, "operfly:RFD900ux-SMT", "U", "RFD900ux-SMT (secenek: RFD868ux-SMT)", 100, 95, {
    "+5V": "+5V3_RADIO", "GND": "GND", "RX": "RADIO_RX_M", "TX": "RADIO_TXD", "RTS": "RADIO_RTS", "CTS": "RADIO_CTS_M",
    "SWO": "RADIO_SWO", "GPIO0": "RADIO_GPIO0_M", "GPIO1/PPM": "RADIO_GPIO1_M",
    "ANT1": "RADIO_ANT1", "ANT2": "RADIO_ANT2", "+3V3_OUT": "RADIO_3V3"}, "operfly_ayak:RFDesign_RFD900ux-SMT")
g = Izgara(50, 160, sutun=9)
for a, b in (("RADIO_RXD", "RADIO_RX_M"), ("RADIO_CTS", "RADIO_CTS_M"), ("RADIO_BOOT_N", "RADIO_SWO"), ("RADIO_GPIO0", "RADIO_GPIO0_M"), ("RADIO_GPIO1", "RADIO_GPIO1_M")):
    k.R(rd, g, "470R", a, b)
k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206); k.C(rd, g, "100n", "+5V3_RADIO"); k.C(rd, g, "100p", "+5V3_RADIO")
g.satir()
for ag in ("RADIO_TXD", "RADIO_RX_M", "RADIO_SWO", "RADIO_3V3"):
    k.olcum_noktasi(rd, g, ag)

rd.metin("ANTENLER: iki giris, modul iyi olani kendisi secer (cesitleme). Hatlar 50 ohm, dogrudan konnektore (uretici onerisi).", 30, 225)
g = Izgara(50, 260, sutun=9)
SMA = "Connector_Coaxial:SMA_Amphenol_132289_EdgeMount"
for i in (1, 2):
    x, y = g.yer(); g.yer()
    k.koy(rd, "Connector:Conn_Coaxial", "J", "ANT %d (SMA)" % i, x + 5, y, {"In": "RADIO_ANT%d" % i, "Ext": "GND"}, SMA)

rd.metin("MODUL BESLEMESI (AP63201, 12 V -> 5,3 V, 2 A, sabit frekansli): modul 5,0-5,5 V ister ve verirken 1 A tepe akim ceker.", 270, 28)
rd.metin("Ayri regulator: (1) gerilim alt sinirin ustunde kalir, (2) verici darbeleri dugumun 5 V rayini sarsmaz,", 270, 34)
rd.metin("(3) islemci modulu kapatip acabilir (modulde sifirlama ucu yok). Cikis = 0,8 V x (1 + 169k / 30k1) = 5,29 V.", 270, 40)
rd.metin("Besleme sifirlamada ACIKTIR: islemci yeniden baslasa da radyo baglantisi kopmaz. Islemci RADIO_OFF = 1 ile keser.", 270, 46)
g = Izgara(290, 86, sutun=9)
k.parca(rd, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+12V", "EN": "RADIO_EN", "GND": "GND", "SW": "SW_RADIO", "BST": "BST_RADIO", "FB": "FB_RADIO"}, "Package_TO_SOT_SMD:TSOT-23-6")
k.R(rd, g, "100k", "+12V", "RADIO_EN"); k.C(rd, g, "10u 50V", "+12V", fp=C1206); k.C(rd, g, "100n", "BST_RADIO", "SW_RADIO")
k.iki(rd, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_RADIO", "+5V3_RADIO", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206); k.C(rd, g, "22u 16V", "+5V3_RADIO", fp=C1206)
g.satir()
k.R(rd, g, "169k 1%", "+5V3_RADIO", "FB_RADIO"); k.R(rd, g, "30k1 1%", "FB_RADIO", "GND"); k.C(rd, g, "100p", "+5V3_RADIO", "FB_RADIO")
k.bayrak(rd, g, "+5V3_RADIO")
x, y = g.yer()
k.koy(rd, "Transistor_FET:2N7002", "Q", "2N7002", x, y, {"D": "RADIO_EN", "S": "GND", "G": "RADIO_OFF"}, "Package_TO_SOT_SMD:SOT-23")
k.R(rd, g, "100k", "RADIO_OFF", "GND")

rd.metin("BESLEME OLCUMU: islemci modul gerilimini okur (10 k / 10 k, 5,3 V -> 2,65 V).", 270, 170)
g = Izgara(290, 205, sutun=9)
k.R(rd, g, "10k 1%", "+5V3_RADIO", "RADIO_VSENS"); k.R(rd, g, "10k 1%", "RADIO_VSENS", "GND"); k.C(rd, g, "100n", "RADIO_VSENS")
rd.yaz(os.path.join(BURASI, "radyo.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_rx.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, rd], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_rx (kok + 2 sayfa)")
