"""Operfly Tracker (anten takip birimi) şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py TRACKER operfly_tracker`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + iki adım motoru sürücüsü (TMC2209-LA: yatay ve dikey eksen) + referans anahtarı girişleri +
isteğe bağlı açı algılayıcı (enkoder) konnektörleri.
Sürücünün uç sırası KiCad kütüphanesindendir; çevre devresi üretilmiş açık kaynaklı bir sürücü kartının şematiğiyle
(aynı entegre, aynı kılıf) karşılaştırılarak çizildi: 5VOUT 4,7 uF, CPI-CPO 22 nF, VCP-VS 100 nF, akım algılama 0,11 ohm,
VREF 2,5 V = 1,77 A RMS. İşlemci pinleri KiCad pin verisindeki alternatif işlevlerle denetlendi.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
TANTAL = "Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D"
R0805 = "Resistor_SMD:R_0805_2012Metric"
k = Kart("operfly_tracker", "2026-11-15")
kok = Sema(k.P, "Operfly Tracker", kagit="A3", tarih=k.T)
kok.metin("Operfly Tracker - anten takip birimi (OPFTRK)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/TRACKER/kicad/uret.py.", 25.4, 33.02, 1.6)

EK = {"PA6": "PAN_STEP", "PA7": "TILT_STEP",              # TIM16_CH1, TIM17_CH1: eksen basina ayri zamanlayici (bagimsiz hiz)
      "PA4": "PAN_DIR", "PA5": "TILT_DIR",
      "PB0": "MOT_EN_N",                                  # 0: suruculer acik (sifirlamada 10k ile kapali)
      "PB6": "TMC_TX", "PB7": "TMC_UART",                 # USART1: iki surucunun tek hatli ayar portu (TX 1k uzerinden ayni hatta)
      "PC6": "PAN_DIAG", "PC7": "TILT_DIAG",              # surucu ariza / yuk algilama cikislari
      "PA0": "PAN_REF", "PA1": "TILT_REF",                # referans anahtarlari (0 = anahtar kapali)
      "PB10": "PAN_SCL", "PB11": "PAN_SDA",               # I2C2: yatay eksen aci algilayicisi (istege bagli)
      "PB3": "TILT_SCL", "PB4": "TILT_SDA"}               # I2C3: dikey eksen aci algilayicisi (istege bagli)
dg = dugum_sayfasi(k, kok, BURASI, ek=EK)

mt = Sema(k.P, "Tracker - motor suruculeri, referans ve aci girisleri", kagit="A1", tarih=k.T, ust=kok, ad="Motor", genel_etiket=True)
kok.alt_sayfa(mt, "motor.kicad_sch", 101.6, 50.8)
mt.metin("ADIM MOTORU SURUCULERI (2 x TMC2209-LA): yatay (PAN) ve dikey (TILT) eksen. Suruculer omurganin korumali 12 V'undan beslenir.", 30, 28)
mt.metin("Cevre devresi uretilmis bir surucu kartindaki gibidir: 5VOUT 4,7 uF, CPI-CPO 22 nF, VCP-VS 100 nF, akim algilama 0,11 ohm.", 30, 34)
mt.metin("Akim: VREF = 5VOUT x 10k / (39k + 10k) = 1,02 V -> faz basina yaklasik 0,7 A RMS (2,5 V = 1,77 A). Yazilim seri porttan dusurebilir.", 30, 40)
mt.metin("Ayar portu tek hattir (iki surucu ayni hatta): adres MS1 ucuyla secilir (PAN = 0, TILT = 1). Islemcinin TX ucu 1k uzerinden hatta baglidir.", 30, 46)
mt.metin("MOT_EN_N sifirlamada 10k ile YUKSEKTIR: islemci acilana kadar motorlara akim verilmez. STDBY, SPREAD ve CLK topraga baglidir.", 30, 52)
VQFN = "Package_DFN_QFN:VQFN-28-1EP_5x5mm_P0.5mm_EP3.7x3.7mm_ThermalVias"
for e, x0, y0, ms1 in (("PAN", 110, 130, "GND"), ("TILT", 110, 330, "+3V3")):
    k.koy(mt, "Driver_Motor:TMC2209-LA", "U", "TMC2209-LA (%s)" % e, x0, y0, {
        "VS": "+12V", "VCC_IO": "+3V3", "GND": "GND", "5VOUT": e + "_5V", "VREF": e + "_VREF", "VCP": e + "_VCP", "CPO": e + "_CPO", "CPI": e + "_CPI",
        "~{EN}": "MOT_EN_N", "STEP": e + "_STEP", "DIR": e + "_DIR", "~{PD}/UART": "TMC_UART", "MS1/AD0": ms1, "MS2/AD1": "GND",
        "SPREAD": "GND", "STDBY": "GND", "CLK": "GND", "DIAG": e + "_DIAG",
        "OA1": e + "_A1", "OA2": e + "_A2", "OB1": e + "_B1", "OB2": e + "_B2", "BRA": e + "_BRA", "BRB": e + "_BRB"}, VQFN)
    g = Izgara(x0 + 70, y0 - 30, sutun=14)
    k.C(mt, g, "100n 50V", "+12V", fp=C0603); k.C(mt, g, "100n 50V", "+12V", fp=C0603); k.C(mt, g, "10u 50V", "+12V", fp=C1206)
    k.C(mt, g, "100u 25V", "+12V", fp=TANTAL)
    k.C(mt, g, "100n 50V", e + "_VCP", "+12V", fp=C0603); k.C(mt, g, "22n 50V", e + "_CPO", e + "_CPI", fp=C0603)
    k.C(mt, g, "4u7 10V", e + "_5V", fp=C0805); k.C(mt, g, "100n", "+3V3")
    k.R(mt, g, "39k 1%", e + "_5V", e + "_VREF"); k.R(mt, g, "10k 1%", e + "_VREF", "GND"); k.C(mt, g, "100n", e + "_VREF")
    k.R(mt, g, "0R11 1% 0,5 W", e + "_BRA", "GND", fp=R0805); k.R(mt, g, "0R11 1% 0,5 W", e + "_BRB", "GND", fp=R0805)
    g.satir()
    k.parca(mt, g, "Connector_Generic:Conn_01x04", "J", "Motor %s (JST-XH: A1, A2, B1, B2)" % e,
            {"Pin_1": e + "_A1", "Pin_2": e + "_A2", "Pin_3": e + "_B1", "Pin_4": e + "_B2"}, "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", bosluk=1, dx=8)
    k.olcum_noktasi(mt, g, e + "_DIAG"); k.olcum_noktasi(mt, g, e + "_VREF")

mt.metin("ORTAK HATLAR: surucu acma ucu ve ayar portu.", 520, 80)
g = Izgara(540, 115, sutun=10)
k.R(mt, g, "10k", "+3V3", "MOT_EN_N"); k.R(mt, g, "1k", "TMC_TX", "TMC_UART"); k.R(mt, g, "100k", "+3V3", "TMC_UART")
k.olcum_noktasi(mt, g, "TMC_UART"); k.olcum_noktasi(mt, g, "MOT_EN_N")

mt.metin("REFERANS ANAHTARLARI (JST-GH 3: +3V3, sinyal, GND): acilista her eksen bilinen bir noktaya gider. Mekanik ya da Hall/optik anahtar olabilir.", 520, 180)
mt.metin("Giris 10k ile yukari cekili, 1k + 100 nF suzgecli; anahtar kapaninca 0 okunur.", 520, 186)
g = Izgara(540, 225, sutun=12)
for e in ("PAN", "TILT"):
    k.parca(mt, g, "Connector_Generic_MountingPin:Conn_01x03_MountingPin", "J", "Referans %s" % e,
            {"Pin_1": "+3V3", "Pin_2": e + "_REF_K", "Pin_3": "GND", "MountPin": "GND"}, "Connector_JST:JST_GH_SM03B-GHS-TB_1x03-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
    k.R(mt, g, "10k", "+3V3", e + "_REF_K"); k.R(mt, g, "1k", e + "_REF_K", e + "_REF"); k.C(mt, g, "100n", e + "_REF")

mt.metin("ACI ALGILAYICI KONNEKTORLERI (istege bagli; JST-GH 4: +3V3, GND, SCL, SDA): mil ucundaki miknatisli aci algilayicilar icin, eksen basina", 520, 290)
mt.metin("ayri I2C hatti (ayni adresli iki algilayici kullanilabilsin diye). Adim kacirmayi yakalar; ruzgarli yerde onerilir.", 520, 296)
g = Izgara(540, 335, sutun=12)
for e in ("PAN", "TILT"):
    k.parca(mt, g, "Connector_Generic_MountingPin:Conn_01x04_MountingPin", "J", "Aci algilayici %s" % e,
            {"Pin_1": "+3V3", "Pin_2": "GND", "Pin_3": e + "_SCL", "Pin_4": e + "_SDA", "MountPin": "GND"},
            "Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal", bosluk=1, dx=8)
    k.R(mt, g, "2k2", "+3V3", e + "_SCL"); k.R(mt, g, "2k2", "+3V3", e + "_SDA")
mt.yaz(os.path.join(BURASI, "motor.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_tracker.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, mt], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_tracker (kok + 2 sayfa)")
