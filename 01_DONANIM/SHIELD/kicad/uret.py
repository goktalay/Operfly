"""Operfly Shield (sürüm 1) arayüz kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py SHIELD operfly_shield`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + hazır karıştırma önleyici anten modülünün beslemesi (12 V -> 18 V yükselten regülatör, sigorta,
anahtar) + modülün seri arayüzü (RS-232 alıcı-verici; dizgi seçeneğiyle 3,3 V doğrudan).
Modülün üretici sayfasında yazanlar: besleme 12-36 V, en çok 8 W, konnektörler J30J-9ZK + SMA-K. Seri arayüzün türü ve
konnektörün uç sırası sayfada YOKTUR; bu yüzden kart tarafındaki konnektör Operfly tanımıdır ve ara kablo modülün
belgesi gelince hazırlanır (README). RF yolu karttan geçmez.
Yükselten regülatör: TPS61175 (SLVS892F: uç tablosu, Tablo 2 ve 3, Denklem 9, tipik uygulama değerleri).
RS-232 alıcı-verici: MAX3232 (3,3 V'ta dört kondansatör 0,1 uF).
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
SOT23 = "Package_TO_SOT_SMD:SOT-23"
k = Kart("operfly_shield", "2026-11-15")
kok = Sema(k.P, "Operfly Shield", kagit="A3", tarih=k.T)
kok.metin("Operfly Shield - karistirma onleyici anten birimi, arayuz karti (OPFSHD, surum 1)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/SHIELD/kicad/uret.py.", 25.4, 33.02, 1.6)

EK = {"PA2": "SHD_TXD", "PA3": "SHD_RXD",                 # USART2_TX -> modul, USART2_RX <- modul
      "PA4": "SHD_PWR_ON",                                # 0: modul beslemesi kapali (sifirlamada 100k ile ACIK)
      "PA5": "SHD_VSENS"}                                 # ADC1_IN5: modul besleme gerilimi / 11
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

md = Sema(k.P, "Shield - modul beslemesi (18 V) ve seri arayuz", kagit="A2", tarih=k.T, ust=kok, ad="Modul", genel_etiket=True)
kok.alt_sayfa(md, "modul.kicad_sch", 101.6, 50.8)
md.metin("MODUL BESLEMESI (TPS61175, 12 V -> 18 V, 1,2 MHz): modul 12-36 V ister; omurganin 12 V'u giris diyodundan sonra bu sinirin altinda", 30, 28)
md.metin("kalabilir, bu yuzden gerilim yukseltilir. Cikis = 1,229 V x (137k / 10k + 1) = 18,1 V. Modul en cok 8 W (0,45 A) ceker.", 30, 34)
md.metin("Frekans direnci 80k6 (1,2 MHz), yumusak kalkis 47 nF, kompanzasyon 10k + 22 nF: ureticinin tipik uygulama degerleri.", 30, 40)
k.koy(md, "operfly:TPS61175", "U", "TPS61175PWP", 90, 100, {
    "VIN": "+12V", "EN": "+3V3", "SYNC": "GND", "FREQ": "BST_FREQ", "SS": "BST_SS", "COMP": "BST_COMP",
    "SW": "BST_SW", "FB": "BST_FB", "NC": "GND", "AGND": "GND", "PGND": "GND"},
    "Package_SO:Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.94x3.34mm_ThermalVias")
g = Izgara(150, 80, sutun=12)
k.C(md, g, "10u 50V", "+12V", fp=C1206); k.C(md, g, "100n 50V", "+12V", fp=C0603)
k.iki(md, g, "Device:L", "L", "10u (Isat >= 3 A)", "+12V", "BST_SW", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.iki(md, g, "Device:D_Schottky", "D", "B360A (60 V, 3 A)", "+18V_SHD", "BST_SW", "Diode_SMD:D_SMA")
k.C(md, g, "10u 50V", "+18V_SHD", fp=C1206); k.C(md, g, "10u 50V", "+18V_SHD", fp=C1206); k.C(md, g, "100n 50V", "+18V_SHD", fp=C0603)
k.R(md, g, "137k 1%", "+18V_SHD", "BST_FB"); k.R(md, g, "10k 1%", "BST_FB", "GND")
k.R(md, g, "80k6 1%", "BST_FREQ", "GND"); k.C(md, g, "47n", "BST_SS")
g.satir()
k.R(md, g, "10k", "BST_COMP", "BST_COMP_RC"); k.C(md, g, "22n", "BST_COMP_RC"); k.olcum_noktasi(md, g, "+18V_SHD")

md.metin("SIGORTA ve ANAHTAR: kendini onaran 0,75 A sigorta, P kanal MOSFET anahtar. Yukselten regulator kapaliyken de girisi cikisa", 30, 170)
md.metin("gecirdigi icin modulu gercekten kapatmak anahtarla yapilir. Anahtar sifirlamada ACIKTIR (islemci yeniden baslasa da konum kesilmez);", 30, 176)
md.metin("islemci SHD_PWR_ON = 0 ile kapatir. Kapi gerilimi 100k / 100k ile yariya bolunur (9 V). SHD_VSENS = modul gerilimi / 11.", 30, 182)
g = Izgara(50, 220, sutun=14)
k.iki(md, g, "Device:Polyfuse", "F", "0,75 A tutma (1812, 30 V)", "+18V_SHD", "+18V_F", "Fuse:Fuse_1812_4532Metric")
x, y = g.yer()
k.koy(md, "Transistor_FET:DMP3099L", "Q", "DMP3099L", x, y, {"S": "+18V_F", "D": "+18V_MOD", "G": "SHD_GATE"}, SOT23)
k.R(md, g, "100k", "+18V_F", "SHD_GATE"); k.C(md, g, "100n 50V", "+18V_F", "SHD_GATE", fp=C0603)
x, y = g.yer()
k.koy(md, "Transistor_FET:2N7002", "Q", "2N7002", x, y, {"D": "SHD_GATE_R", "S": "GND", "G": "SHD_PWR_ON"}, SOT23)
k.R(md, g, "100k", "SHD_GATE", "SHD_GATE_R"); k.R(md, g, "100k", "+3V3", "SHD_PWR_ON")
k.C(md, g, "10u 50V", "+18V_MOD", fp=C1206); k.iki(md, g, "Device:D_TVS", "D", "SMBJ20A", "+18V_MOD", "GND", "Diode_SMD:D_SMB")
k.R(md, g, "100k 1%", "+18V_MOD", "SHD_VSENS"); k.R(md, g, "10k 1%", "SHD_VSENS", "GND"); k.C(md, g, "100n", "SHD_VSENS")
k.olcum_noktasi(md, g, "+18V_MOD")

md.metin("SERI ARAYUZ: modulun seri arayuz turu uretici sayfasinda yazmiyor. Ayni siniftaki urunlerde RS-232 oldugu icin RS-232 alici-verici", 300, 170)
md.metin("(MAX3232, 4 x 100 nF) cizildi. Arayuz 3,3 V cikarsa: MAX3232 ve R(232) direncleri dizilmez, DNP isaretli 0R'ler dizilir.", 300, 176)
md.metin("IKISI BIRDEN DIZILMEZ: RS-232 gerilimleri (+/-6 V) islemciye zarar verir.", 300, 182)
k.koy(md, "Interface_UART:MAX3232", "U", "MAX3232IPW", 350, 250, {
    "VCC": "+3V3", "GND": "GND", "C1+": "RS_C1P", "C1-": "RS_C1N", "C2+": "RS_C2P", "C2-": "RS_C2N", "VS+": "RS_VP", "VS-": "RS_VN",
    "T1IN": "SHD_TXD", "T1OUT": "RS_TX", "R1IN": "RS_RX", "R1OUT": "SHD_RXD", "T2IN": "GND"}, "Package_SO:TSSOP-16_4.4x5mm_P0.65mm")
g = Izgara(420, 220, sutun=10)
k.C(md, g, "100n", "RS_C1P", "RS_C1N"); k.C(md, g, "100n", "RS_C2P", "RS_C2N"); k.C(md, g, "100n", "RS_VP"); k.C(md, g, "100n", "RS_VN"); k.C(md, g, "100n", "+3V3")
g.satir()
k.R(md, g, "0R (232)", "RS_TX", "MOD_TX"); k.R(md, g, "0R (232)", "MOD_RX", "RS_RX")
k.R(md, g, "0R (3V3)", "SHD_TXD", "MOD_TX", dnp=True); k.R(md, g, "0R (3V3)", "MOD_RX", "SHD_RXD", dnp=True)
k.olcum_noktasi(md, g, "MOD_TX"); k.olcum_noktasi(md, g, "MOD_RX")

md.metin("MODUL KONNEKTORU (JST-GH 6, Operfly tanimi): 1-2 +18 V, 3-4 GND, 5 kart -> modul, 6 modul -> kart. Modulun kendi konnektorune", 300, 320)
md.metin("(J30J-9ZK) giden ara kablo, satici uc sirasini bildirince hazirlanir. RF cikisi (SMA) koaksiyel kabloyla dogrudan Nav'a gider.", 300, 326)
g = Izgara(320, 365, sutun=10)
k.parca(md, g, "Connector_Generic_MountingPin:Conn_01x06_MountingPin", "J", "Modul (besleme + seri)", {
    "Pin_1": "+18V_MOD", "Pin_2": "+18V_MOD", "Pin_3": "GND", "Pin_4": "GND", "Pin_5": "MOD_TX", "Pin_6": "MOD_RX", "MountPin": "GND"},
    "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
md.yaz(os.path.join(BURASI, "modul.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_shield.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, md], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_shield (kok + 2 sayfa)")
