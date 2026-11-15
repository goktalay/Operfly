"""Operfly Cell şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py CELL operfly_cell`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Kart: düğüm devresi + M.2 Key B 5G modem yuvası (aday: Quectel RM520N-GL, 30x52 mm) + modem beslemesi (3,8 V, 5 A)
+ PCIe gigabit Ethernet denetleyici (RTL8111H) + omurga Ethernet'i + iki nano-SIM + servis USB'si.

Veri yolu: modem PCIe'yi kök (RC) kipinde çalıştırır ve karttaki Ethernet denetleyiciyi kendisi sürer; omurgaya
bakır Ethernet olarak çıkar. Düğüm işlemcisi veri taşımaz; modemi açar, kapatır, sıfırlar ve USB üzerinden AT komutlarıyla izler.
Uç sıraları: modem ve M.2 yuvası üretici donanım tasarım kılavuzundan (RM520N-GL Hardware Design V1.0, Tablo 5),
Ethernet denetleyici üretici veri sayfasından, diğerleri KiCad kütüphanesinden.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C1206, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
C1210 = "Capacitor_SMD:C_1210_3225Metric"
TANTAL = "Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D"
N7002 = ("Transistor_FET:2N7002", "Q", "2N7002", "Package_TO_SOT_SMD:SOT-23")
TRAFO = "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13"
V38, V33E = "+3V8_MODEM", "+3V3_ETH"

k = Kart("operfly_cell", "2026-11-15")
kok = Sema(k.P, "Operfly Cell", kagit="A3", tarih=k.T)
kok.metin("Operfly Cell - 5G hucresel baglanti karti (OPFCEL)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/CELL/kicad/uret.py. Modem M.2 yuvasina takilir; anten kablolari modulun kendi konnektorlerinden cikar.", 25.4, 33.02, 1.6)

EK = {"PA9/PA11": "MCU_USB_DM", "PA10/PA12": "MCU_USB_DP",   # USB FS ana bilgisayar (PA11 = D-, PA12 = D+): modemin AT kanali
      "PA4": "MODEM_PWR_OFF",                                # 1: modem regulatorunu kapat (sifirlamada acik)
      "PA5": "MODEM_ON",                                     # FULL_CARD_POWER_OFF#: 1 = modem calisir, 0 = kapanir (sifirlamada 0)
      "PA6": "MODEM_RST",                                    # 1: RESET# dusuge cekilir
      "PA7": "MODEM_RF_EN",                                  # W_DISABLE1#: 0 = radyo kapali (ucak kipi); acik savak sur
      "PB0": "MODEM_WAKE_N",                                 # WAKE_ON_WAN#: modem bildirimi (1 s dusuk darbe)
      "PA0": "MODEM_VSENS",                                  # ADC1_IN0: modem beslemesi / 2
      "PA1": "USB_SEL",                                      # 1: servis USB'sine kablo takili (modemin USB'si oraya bagli)
      "PB3": "ETH_PG"}                                       # 1: Ethernet denetleyicinin 3,3 V'u hazir
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, ethernet=True)

# --- Modem: besleme, M.2 yuvası, denetim, SIM, USB ----------------------------------
md = Sema(k.P, "Operfly Cell - modem beslemesi, M.2 yuvasi, SIM, servis USB'si", kagit="A1", tarih=k.T, ust=kok, ad="Modem", genel_etiket=True)
kok.alt_sayfa(md, "modem.kicad_sch", 101.6, 50.8)
md.metin("MODEM BESLEMESI (TPS54560B, 400 kHz): omurga 12 V'undan 3,8 V / 5 A. Modem 3,135-4,4 V ister, verici patlamalarinda 3 A ceker.", 30, 28)
md.metin("Cikis 3,80 V (38k3 / 10k2). Giris 9,0 V'ta acar, 8,0 V'ta kapatir (294k / 43k2). Varsayilan ACIK; islemci MODEM_PWR_OFF ile kapatir.", 30, 34)
md.metin("KURAL: besleme, modem FULL_CARD_POWER_OFF# ile kapatilip 1 s beklenmeden KESILMEZ (modemin dahili bellegi bozulabilir).", 30, 40)
g = Izgara(50, 80, sutun=16, dx=24)
k.parca(md, g, "Regulator_Switching:TPS54560BDDA", "U", "TPS54560BDDAR", {"VIN": "+12V", "EN": "MDM_EN", "RT/CLK": "MDM_RT", "FB": "MDM_FB",
        "COMP": "MDM_COMP", "BOOT": "MDM_BOOT", "SW": "MDM_SW", "GND": "GND"},
        "Package_SO:Texas_R-PDSO-G8_EP2.95x4.9mm_Mask2.4x3.1mm_ThermalVias", bosluk=2, dx=22)
k.C(md, g, "10u 50V", "+12V", fp=C1206); k.C(md, g, "10u 50V", "+12V", fp=C1206); k.C(md, g, "100n 50V", "+12V", fp=C0603)
k.R(md, g, "294k 1%", "+12V", "MDM_EN"); k.R(md, g, "43k2 1%", "MDM_EN", "GND")
k.R(md, g, "243k 1%", "MDM_RT", "GND")
k.R(md, g, "26k7", "MDM_COMP", "MDM_COMP_RC"); k.C(md, g, "15n", "MDM_COMP_RC"); k.C(md, g, "220p", "MDM_COMP")
k.C(md, g, "100n 25V", "MDM_BOOT", "MDM_SW", fp=C0603)
k.iki(md, g, "Device:D_Schottky", "D", "PDS760 (60 V, 7 A)", "MDM_SW", "GND", "Diode_SMD:D_PowerDI-5")
k.iki(md, g, "Device:L", "L", "10u XAL7070-103", "MDM_SW", V38, "Inductor_SMD:L_Coilcraft_XAL7070-XXX")
g.satir()
k.C(md, g, "47u 16V", V38, fp=C1210); k.C(md, g, "47u 16V", V38, fp=C1210)
k.R(md, g, "38k3 1%", V38, "MDM_FB"); k.R(md, g, "10k2 1%", "MDM_FB", "GND")
k.R(md, g, "10k 1%", V38, "MODEM_VSENS"); k.R(md, g, "10k 1%", "MODEM_VSENS", "GND"); k.C(md, g, "100n", "MODEM_VSENS")
x, y = g.yer()
k.koy(md, *N7002[:3], x, y, {"D": "MDM_EN", "S": "GND", "G": "MODEM_PWR_OFF"}, N7002[3])
k.R(md, g, "100k", "MODEM_PWR_OFF", "GND")
k.bayrak(md, g, V38); k.olcum_noktasi(md, g, V38)

md.metin("MODEM YUVASI (M.2 Key B, 3052): uc numaralari modem kilavuzundaki gibidir. Yuva sembolundeki adlar bilgisayar tarafina goredir:", 30, 150)
md.metin("41/43 modemin PCIe VERICISI, 47/49 modemin PCIe ALICISI. Modem kok (RC) kipinde: PCIE_RST_N ve saat modemden cikar.", 30, 156)
md.metin("VCC yaninda: 2 x 220 uF dusuk ESR + seramik dizi + 5 V kirpma diyodu (uretici onerisi). Bos birakilan uclar kilavuza gore bos kalir.", 30, 162)
S = {"3.3V": V38, "GND": "GND", "~{FULL_CARD_POWER_OFF}": "MODEM_ON", "~{RESET}": "MODEM_RESET_N", "~{W_DISABLE1}": "MODEM_RF_EN",
     "USB_D+": "MODEM_USB_DP_M", "USB_D-": "MODEM_USB_DM_M", "10": "MODEM_LED_N", "23": "MODEM_WAKE_N",
     "UIM-PWR": "USIM1_VDD", "UIM-RESET": "USIM1_RST", "UIM-CLK": "USIM1_CLK", "UIM-DATA": "USIM1_DATA",
     "48": "USIM2_VDD_M", "46": "USIM2_RST_M", "44": "USIM2_CLK_M", "42": "USIM2_DATA_M",
     "43": "PCIE_MTX_P", "41": "PCIE_MTX_N", "49": "PCIE_MRX_P", "47": "PCIE_MRX_N",
     "~{PERST}": "PCIE_RST_N", "~{CLKREQ}": "PCIE_CLKREQ_N", "~{PEWAKE}": "PCIE_WAKE_N", "REFCLKp": "PCIE_CLK_P", "REFCLKn": "PCIE_CLK_N"}
k.koy(md, "Connector:Bus_M.2_Socket_B", "J", "M.2 Key B (5G modem, 3052)", 100, 250, S, "Connector_PCBEdge:TE_M.2_B_2x38-1MP_P0.5mm")
g = Izgara(180, 200, sutun=14)
k.C(md, g, "220u 6V3 polimer", V38, fp=TANTAL); k.C(md, g, "220u 6V3 polimer", V38, fp=TANTAL)
for deger in ("100n", "100n", "6n8", "220p", "220p", "68p", "68p", "15p", "9p1", "4p7"):
    k.C(md, g, deger, V38)
k.iki(md, g, "Device:D_TVS", "D", "SMAJ5.0A", V38, "GND", "Diode_SMD:D_SMA")
g.satir()
x, y = g.yer()
k.koy(md, *N7002[:3], x, y, {"D": "MODEM_RESET_N", "S": "GND", "G": "MODEM_RST"}, N7002[3])
k.R(md, g, "100k", "MODEM_RST", "GND"); k.R(md, g, "100k", "MODEM_ON", "GND")
k.R(md, g, "10k", "+3V3", "MODEM_RF_EN"); k.R(md, g, "10k", "+3V3", "MODEM_WAKE_N")
k.iki(md, g, "Device:LED", "D", "LED mavi (radyo acik)", "MODEM_LED_N", "MODEM_LED_A", "LED_SMD:LED_0603_1608Metric"); k.R(md, g, "330R", V38, "MODEM_LED_A")
k.olcum_noktasi(md, g, "MODEM_RESET_N"); k.olcum_noktasi(md, g, "MODEM_ON")

md.metin("SIM KARTLAR (2 x nano-SIM, cift operator, ayni anda biri etkin): 22R seri, 10 pF, veri hattinda 15k yukari cekme, dusuk sigali", 180, 290)
md.metin("koruma dizisi (uretici onerisi). Kart algilama kullanilmaz (ucusta sicak takma yok). Ikinci yuva ileride lehimli eSIM ile degisebilir.", 180, 296)
for n in (1, 2):
    p = "USIM%d" % n
    g = Izgara(200, 335 + (n - 1) * 90, sutun=14)
    k.parca(md, g, "Connector:SIM_Card_Shielded", "J", "nano-SIM %d" % n, {"VCC": p + "_VDD", "RST": p + "_RST_K", "CLK": p + "_CLK_K", "I/O": p + "_DATA_K",
            "GND": "GND", "SH": "GND"}, "Connector_Card:nanoSIM_GCT_SIM8060-6-0-14-00", bosluk=2, dx=18)
    for s_ in ("RST", "CLK", "DATA"):
        k.R(md, g, "22R", "%s_%s" % (p, s_), "%s_%s_K" % (p, s_))
    k.R(md, g, "15k", p + "_VDD", p + "_DATA_K")
    if n == 2:   # uretici onerisi: modemin yaninda 0R; dahili eSIM'li modem takilirsa bu direncler dizilmez
        for s_ in ("VDD", "RST", "CLK", "DATA"):
            k.R(md, g, "0R", "USIM2_%s_M" % s_, "USIM2_%s" % s_)
    k.C(md, g, "100n", p + "_VDD")
    for s_ in ("RST", "CLK", "DATA"):
        k.C(md, g, "10p", "%s_%s_K" % (p, s_))
    k.bayrak(md, g, p + "_VDD")
    g.satir()
    k.parca(md, g, "Power_Protection:TPD4E05U06DQA", "D", "TPD4E05U06DQA", {"D1+": p + "_VDD", "D1-": p + "_RST_K", "D2+": p + "_CLK_K", "D2-": p + "_DATA_K", "GND": "GND"},
            "Package_SON:USON-10_2.5x1.0mm_P0.5mm", bosluk=2, dx=18)

md.metin("MODEM USB'si (USB 2.0): AT komutlari ve modem yazilimi guncellemesi yalnizca buradan yapilir. Anahtar (FSUSB42) hatti iki yere verir:", 480, 290)
md.metin("kablo takili degilken dugum islemcisine (USB ana bilgisayar, AT komutlari), servis USB'sine kablo takilinca (VBUS gelince) bilgisayara.", 480, 296)
md.metin("Servis USB'si karti BESLEMEZ; modem ayarlanirken ya da guncellenirken kart omurgadan beslenmelidir.", 480, 302)
g = Izgara(500, 335, sutun=12)
k.R(md, g, "0R", "MODEM_USB_DP_M", "MODEM_USB_DP"); k.R(md, g, "0R", "MODEM_USB_DM_M", "MODEM_USB_DM")
k.parca(md, g, "Interface_USB:FSUSB42MUX", "U", "FSUSB42MUX", {"VCC": "+3V3", "GND": "GND", "SEL": "USB_SEL", "~{OE}": "GND", "D+": "MODEM_USB_DP", "D-": "MODEM_USB_DM",
        "HSD1+": "MCU_USB_DP", "HSD1-": "MCU_USB_DM", "HSD2+": "SVC_USB_DP", "HSD2-": "SVC_USB_DM"}, "Package_SO:MSOP-10_3x3mm_P0.5mm", bosluk=2, dx=18)
k.C(md, g, "100n", "+3V3")
k.R(md, g, "15k", "MCU_USB_DP", "GND", dnp=True); k.R(md, g, "15k", "MCU_USB_DM", "GND", dnp=True)
k.R(md, g, "100k", "USB_VBUS", "USB_SEL"); k.R(md, g, "100k", "USB_SEL", "GND"); k.C(md, g, "100n", "USB_SEL")
g.satir(); g.satir()
k.parca(md, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C (servis)", {"VBUS": "USB_VBUS", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2",
        "D+": "SVC_USB_DP", "D-": "SVC_USB_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
k.koy(md, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "SVC_USB_DP", "6": "SVC_USB_DP", "3": "SVC_USB_DM", "4": "SVC_USB_DM", "5": "USB_VBUS", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
k.R(md, g, "5k1 1%", "USB_CC1", "GND"); k.R(md, g, "5k1 1%", "USB_CC2", "GND"); k.C(md, g, "1u 25V", "USB_VBUS", fp=C0603)
md.yaz(os.path.join(BURASI, "modem.kicad_sch"))

# --- Ethernet: 3,3 V, PCIe Ethernet denetleyici, trafo -------------------------------
et = Sema(k.P, "Operfly Cell - PCIe Ethernet denetleyici ve omurga Ethernet'i", kagit="A1", tarih=k.T, ust=kok, ad="Ethernet", genel_etiket=True)
kok.alt_sayfa(et, "ethernet.kicad_sch", 177.8, 50.8)
et.metin("3,3 V (TPS62130, 5 V'tan): yalnizca Ethernet denetleyici icin. Modem beslemesi gelince acar; modem beslemesi yokken denetleyici", 30, 28)
et.metin("ve PCIe yukari cekme direncleri de gerilimsiz kalir (kapali modemin uclarina gerilim verilmez).", 30, 34)
g = Izgara(50, 75, sutun=14)
k.parca(et, g, "Regulator_Switching:TPS62130", "U", "TPS62130RGTR", {"VIN": "+5V", "EN": V38, "GND": "GND", "SW": "REG33E_SW", "VOS": V33E, "FB": "REG33E_FB",
        "SS/TR": "REG33E_SS", "DEF": "GND", "FSW": "GND", "PG": "ETH_PG"}, "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias", bosluk=2, dx=20)
k.C(et, g, "10u 25V", "+5V", fp=C1206); k.C(et, g, "100n 25V", "+5V", fp=C0603)
k.iki(et, g, "Device:L", "L", "2u2 XAL4020-222", "REG33E_SW", V33E, "Inductor_SMD:L_Coilcraft_XAL4020-XXX")
k.C(et, g, "22u 10V", V33E, fp=C1206); k.C(et, g, "22u 10V", V33E, fp=C1206)
k.R(et, g, "316k 1%", V33E, "REG33E_FB"); k.R(et, g, "100k 1%", "REG33E_FB", "GND"); k.C(et, g, "3n3", "REG33E_SS")
k.R(et, g, "100k", "+3V3", "ETH_PG")
k.olcum_noktasi(et, g, V33E); k.bayrak(et, g, V33E)

et.metin("PCIe ETHERNET DENETLEYICI (RTL8111H-CG, 1 Gbit): modem PCIe kok aygitidir, bu entegreyi kendisi surer (modemde AT komutuyla acilir).", 30, 130)
et.metin("Modemin vericisi (41/43) dogrudan HSIP/HSIN'e gelir (kondansator modemin icinde); denetleyicinin vericisi 220 nF ile modemin alicisina gider.", 30, 136)
et.metin("PCIE_RST_N kok kipinde modemin acik savak cikisidir: 4k7 yukari cekme. Cevre degerleri (RSET, 1,0 V kondansatorleri, ISOLATEB) README'de 'dogrulanacak'.", 30, 142)
E = {"HSIP": "PCIE_MTX_P", "HSIN": "PCIE_MTX_N", "HSOP": "ETH_TX_P", "HSON": "ETH_TX_N", "REFCLK_P": "PCIE_CLK_P", "REFCLK_N": "PCIE_CLK_N",
     "PERSTB": "PCIE_RST_N", "CLKREQB": "PCIE_CLKREQ_N", "LANWAKEB": "PCIE_WAKE_N", "ISOLATEB": "ETH_ISOLATE_N",
     "CKXTAL1": "ETH_XI", "CKXTAL2": "ETH_XO", "RSET": "ETH_RSET", "LED0": "ETH_LED0", "LED2": "ETH_LED2", "REGOUT": "ETH_1V0",
     "AVDD33": V33E, "VDDREG": V33E, "AVDD10": "ETH_1V0", "DVDD10": "ETH_1V0", "GND": "GND"}
for i in range(4):
    E["MDIP%d" % i], E["MDIN%d" % i] = "ETH_MDI%d_P" % i, "ETH_MDI%d_N" % i
k.koy(et, "operfly:RTL8111H", "U", "RTL8111H-CG", 110, 230, E, "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.9x2.9mm_ThermalVias")
g = Izgara(50, 300, sutun=14)
k.C(et, g, "220n", "ETH_TX_P", "PCIE_MRX_P"); k.C(et, g, "220n", "ETH_TX_N", "PCIE_MRX_N")
k.R(et, g, "4k7", V33E, "PCIE_RST_N"); k.R(et, g, "10k", V33E, "PCIE_CLKREQ_N"); k.R(et, g, "10k", V33E, "PCIE_WAKE_N")
k.R(et, g, "1k", V33E, "ETH_ISOLATE_N"); k.R(et, g, "15k", "ETH_ISOLATE_N", "GND")
k.R(et, g, "2k49 1%", "ETH_RSET", "GND")
k.koy(et, "Device:Crystal_GND24", "Y", "25 MHz 30 ppm", *g.yer(), {"1": "ETH_XI", "3": "ETH_XO", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(et, g, "27p", "ETH_XI"); k.C(et, g, "27p", "ETH_XO")
g.satir()
for _ in range(3):
    k.C(et, g, "100n", V33E)
k.C(et, g, "4u7", V33E, fp=C0603)
for _ in range(4):
    k.C(et, g, "100n", "ETH_1V0")
k.C(et, g, "4u7", "ETH_1V0", fp=C0603)
for led, renk in (("ETH_LED0", "yesil"), ("ETH_LED2", "sari")):
    k.iki(et, g, "Device:LED", "D", "LED %s (Ethernet)" % renk, led, led + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(et, g, "510R", V33E, led + "_A")

et.metin("TRAFO (TG111-MSC13LF) ve OMURGA ETHERNET'i: dort cift omurga fisine gider (Hub'in anahtarina). Orta uclar: entegre tarafi 100n -> GND,", 260, 150)
et.metin("kablo tarafi 75R -> 1 nF 2 kV (Vision ve Hub ile ayni).", 260, 156)
tr = {}
for c, i, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", range(4), ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
    tr.update({str(cp): "ETH_MDI%d_P" % i, str(cm): "ETH_MDI%d_N" % i, str(cc): "ETH_CT_%s" % c,
               str(kp_): "ETH_%s+" % c, str(km_): "ETH_%s-" % c, str(kc_): "ETH_KCT_%s" % c})
k.koy(et, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", 300, 230, tr, TRAFO)
g = Izgara(370, 200, sutun=9, dx=24)
for c in "ABCD":
    k.C(et, g, "100n", "ETH_CT_%s" % c)
for c in "ABCD":
    k.R(et, g, "75R", "ETH_KCT_%s" % c, "ETH_BS")
k.C(et, g, "1n 2kV", "ETH_BS", fp=C1206)
et.yaz(os.path.join(BURASI, "ethernet.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_cell.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, md, et], {"operfly": ORTAK_URI})
print("yazildi: operfly_cell (kok + 3 sayfa)")
