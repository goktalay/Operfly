"""Operfly PC adaptörü şematiğini üretir.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py PC_ADAPTOR operfly_pc_adaptor`.
Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: USB Type-C -> USB göbeği -> (1) USB-gigabit Ethernet köprüsü -> omurga fişi, (2) düğüm işlemcisi (CAN FD geçidi).
Kart USB'den beslenir; omurgaya 12 V vermez.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, XAL, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
FB = "Inductor_SMD:L_0603_1608Metric"
k = Kart("operfly_pc_adaptor", "2026-11-15")
kok = Sema(k.P, "Operfly PC adaptoru", kagit="A3", tarih=k.T)
kok.metin("Operfly PC adaptoru (OPFPCA)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/PC_ADAPTOR/kicad/uret.py", 25.4, 33.02, 1.6)

# Düğüm: USB'den beslenir, omurga fişinde Ethernet çiftleri var, CAN 120 ohm sonlandırılır. İşlemcinin USB'si göbeğin 2. portunda.
EK = {"PA9/PA11": "USB2_DM", "PA10/PA12": "USB2_DP"}       # USB FS: PA11 = D-, PA12 = D+
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, ethernet=True, sonlandirma=120, besleme="harici")

# --- USB: konnektör, göbek, beslemeler, sıfırlama ------------------------------
ub = Sema(k.P, "Operfly PC adaptoru - USB, gobek, beslemeler", kagit="A1", tarih=k.T, ust=kok, ad="USB", genel_etiket=True)
kok.alt_sayfa(ub, "usb.kicad_sch", 101.6, 50.8)
ub.metin("USB TYPE-C GIRISI: kart USB'den beslenir (yaklasik 2 W). Sigorta + ferrit; VBUS uzerinde buyuk kondansator yok (USB ani akim siniri).", 30, 28)
g = Izgara(50, 85, sutun=14)
k.parca(ub, g, "Connector:USB_C_Receptacle_USB2.0_16P", "J", "USB Type-C", {"VBUS": "VBUS_USB", "GND": "GND", "SHIELD": "GND", "CC1": "USB_CC1", "CC2": "USB_CC2",
        "D+": "USB_UP_DP", "D-": "USB_UP_DM"}, "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal", bosluk=2, dx=10)
x, y = g.yer(); g.yer()
k.koy(ub, "Power_Protection:USBLC6-2P6", "D", "USBLC6-2P6", x + 10, y, {"1": "USB_UP_DP", "6": "USB_UP_DP", "3": "USB_UP_DM", "4": "USB_UP_DM", "5": "VBUS_USB", "2": "GND"},
      "Package_TO_SOT_SMD:SOT-666")
k.R(ub, g, "5k1", "USB_CC1", "GND"); k.R(ub, g, "5k1", "USB_CC2", "GND")
k.iki(ub, g, "Device:Polyfuse", "F", "1 A (kendini onaran)", "VBUS_USB", "VBUS_F", "Fuse:Fuse_1812_4532Metric")
k.iki(ub, g, "Device:FerriteBead", "FB", "2 A ferrit", "VBUS_F", "+5V", "Inductor_SMD:L_0805_2012Metric")
k.C(ub, g, "4u7 16V", "+5V", fp=C0805); k.C(ub, g, "100n", "+5V"); k.bayrak(ub, g, "+5V")

ub.metin("BESLEMELER: 5 V -> 3,3 V ve 5 V -> 1,2 V (iki TPS62130). Ethernet koprusunun 1,2 V hatti yaklasik 0,46 A, 3,3 V hatti yaklasik 0,21 A ceker.", 30, 150)
for i, (ag, rust, ralt) in enumerate((("+3V3", "316k 1%", "100k 1%"), ("+1V2", "100k 1%", "200k 1%"))):
    g = Izgara(50, 185 + i * 60, sutun=14)
    n = "REG" + ag.replace("+", "_")
    k.parca(ub, g, "Regulator_Switching:TPS62130", "U", "TPS62130RGTR", {"VIN": "+5V", "EN": "+5V", "GND": "GND", "SW": n + "_SW", "VOS": ag,
            "FB": n + "_FB", "SS/TR": n + "_SS", "DEF": "GND", "FSW": "GND"}, "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias", bosluk=2, dx=20)
    k.C(ub, g, "10u 16V", "+5V", fp=C0805); k.C(ub, g, "100n", "+5V")
    k.iki(ub, g, "Device:L", "L", "2u2 XAL4020-222", n + "_SW", ag, XAL)
    k.C(ub, g, "22u 10V", ag, fp=C1206); k.C(ub, g, "22u 10V", ag, fp=C1206)
    k.R(ub, g, rust, ag, n + "_FB"); k.R(ub, g, ralt, n + "_FB", "GND"); k.C(ub, g, "3n3", n + "_SS")
    k.bayrak(ub, g, ag)

ub.metin("SIFIRLAMA: 3,3 V yaklasik 3,0 V'u gecene kadar gobek ve Ethernet koprusu sifirda tutulur.", 30, 305)
g = Izgara(50, 335, sutun=14)
k.parca(ub, g, "Power_Supervisor:TPS3808DBV", "U", "TPS3808G01DBVR", {"VDD": "+3V3", "GND": "GND", "SENSE": "RST_SENSE", "~{RESET}": "USB_RESET_N"}, "Package_TO_SOT_SMD:SOT-23-6", dx=15)
k.R(ub, g, "64k9 1%", "+3V3", "RST_SENSE"); k.R(ub, g, "10k 1%", "RST_SENSE", "GND"); k.R(ub, g, "10k", "+3V3", "USB_RESET_N"); k.C(ub, g, "100n", "+3V3")

ub.metin("USB GOBEGI (USB2514B, 24 MHz): 1. port Ethernet koprusu, 2. port dugum islemcisi; 3. ve 4. portlar 10 k yukari cekmeyle kapali.", 420, 28)
ub.metin("Kayis uclari: veri yolundan beslenen gobek, 1. ve 2. portlar cikarilamaz aygit (ayar tablosu uretici belgesiyle dogrulanacak).", 420, 34)
k.koy(ub, "Interface_USB:USB2514B_Bi", "U", "USB2514Bi-AEZG", 520, 120, {
    "USBDP_UP": "USB_UP_DP", "USBDM_UP": "USB_UP_DM", "USBDP_DN1/PRT_DIS_P1": "USB1_DP", "USBDM_DN1/PRT_DIS_M1": "USB1_DM",
    "USBDP_DN2/PRT_DIS_P2": "USB2_DP", "USBDM_DN2/PRT_DIS_M2": "USB2_DM", "USBDP_DN3/PRT_DIS_P3": "HUB_DIS3P", "USBDM_DN3/PRT_DIS_M3": "HUB_DIS3M",
    "USBDP_DN4/PRT_DIS_P4": "HUB_DIS4P", "USBDM_DN4/PRT_DIS_M4": "HUB_DIS4M",
    "VDD33": "+3V3", "VDDA33": "+3V3", "VSS": "GND", "TEST": "GND", "RESET_N": "USB_RESET_N", "VBUS_DET": "HUB_VBUS_DET",
    "CRFILT": "HUB_CRFILT", "PLLFILT": "HUB_PLLFILT", "RBIAS": "HUB_RBIAS", "XTALIN/CLKIN": "HUB_XI", "XTALOUT": "HUB_XO",
    "HS_IND/CFG_SEL1": "HUB_CFG1", "SCL/SMBCLK/CFG_SEL0": "HUB_CFG0", "SDA/SMBDATA/NON_REM1": "HUB_NR1", "SUSP_IND/LOCAL_PWR/NON_REM0": "HUB_NR0",
}, "Package_DFN_QFN:QFN-36-1EP_6x6mm_P0.5mm_EP3.7x3.7mm")
g = Izgara(430, 220, sutun=14)
k.koy(ub, "Device:Crystal_GND24", "Y", "24 MHz", *g.yer(), {"1": "HUB_XI", "3": "HUB_XO", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(ub, g, "18p", "HUB_XI"); k.C(ub, g, "18p", "HUB_XO")
k.R(ub, g, "12k 1%", "HUB_RBIAS", "GND"); k.C(ub, g, "100n", "HUB_CRFILT"); k.C(ub, g, "100n", "HUB_PLLFILT")
k.R(ub, g, "1k", "+3V3", "HUB_VBUS_DET")
k.R(ub, g, "100k", "+3V3", "HUB_CFG1"); k.R(ub, g, "100k", "HUB_CFG0", "GND"); k.R(ub, g, "100k", "+3V3", "HUB_NR1"); k.R(ub, g, "100k", "HUB_NR0", "GND")
g.satir()
for a in ("HUB_DIS3P", "HUB_DIS3M", "HUB_DIS4P", "HUB_DIS4M"):
    k.R(ub, g, "10k", "+3V3", a)
for _ in range(6):
    k.C(ub, g, "100n", "+3V3")
k.C(ub, g, "4u7", "+3V3", fp=C0603)
ub.yaz(os.path.join(BURASI, "usb.kicad_sch"))

# --- Ethernet köprüsü: LAN7500 + trafo ----------------------------------------
et = Sema(k.P, "Operfly PC adaptoru - USB-gigabit Ethernet koprusu", kagit="A1", tarih=k.T, ust=kok, ad="Ethernet", genel_etiket=True)
kok.alt_sayfa(et, "ethernet.kicad_sch", 177.8, 50.8)
et.metin("ETHERNET KOPRUSU (LAN7500i, 25 MHz): baglantilar ureticinin sematik denetim listesine gore. Icinde regulator yok; tum beslemeler dis.", 30, 28)
et.metin("EEPROM yok: MAC adresi yazilimdan verilir (kalici adres icin EEPROM sonraki revizyonda). JTAG ve GPIO uclari bos.", 30, 34)
k.koy(et, "Interface_Ethernet:LAN7500-ABJZ", "U", "LAN7500i-ABZJ", 130, 150, {
    "USBDP": "USB1_DP", "USBDM": "USB1_DM", "VBUS_DET": "ETH_VDD33A", "USBRBIAS": "ETH_USBRBIAS", "ETHRBIAS": "ETH_RBIAS",
    "XI": "ETH_XI", "XO": "ETH_XO", "TEST": "GND", "~{RESET}": "USB_RESET_N", "GND": "GND",
    "VDD33A": "ETH_VDD33A", "VDDVARIO": "+3V3", "VDD12CORE": "+1V2", "VDD12BIAS": "+1V2", "VDD12A": "ETH_VDD12A", "VDD12USBPLL": "ETH_VDD12USB", "VDD12PLL": "ETH_VDD12PLL",
    "TR0P": "MDI_A+", "TR0N": "MDI_A-", "TR1P": "MDI_B+", "TR1N": "MDI_B-", "TR2P": "MDI_C+", "TR2N": "MDI_C-", "TR3P": "MDI_D+", "TR3N": "MDI_D-",
}, "Package_DFN_QFN:QFN-56-1EP_8x8mm_P0.5mm_EP5.9x5.9mm")
g = Izgara(240, 80, sutun=14)
k.koy(et, "Device:Crystal_GND24", "Y", "25 MHz", *g.yer(), {"1": "ETH_XI", "3": "ETH_XO", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
k.C(et, g, "18p", "ETH_XI"); k.C(et, g, "18p", "ETH_XO")
k.R(et, g, "8k06 1%", "ETH_RBIAS", "GND"); k.R(et, g, "12k 1%", "ETH_USBRBIAS", "GND")
for ag in ("ETH_VDD33A", "ETH_VDD12A", "ETH_VDD12USB", "ETH_VDD12PLL"):
    k.iki(et, g, "Device:FerriteBead", "FB", "BLM18PG221", "+3V3" if ag == "ETH_VDD33A" else "+1V2", ag, FB)
g.satir()
for ag, adet in (("+3V3", 4), ("+1V2", 7), ("ETH_VDD33A", 1), ("ETH_VDD12A", 4), ("ETH_VDD12USB", 1), ("ETH_VDD12PLL", 1)):
    for _ in range(adet):
        k.C(et, g, "10n", ag)
g.satir()
for ag in ("+3V3", "+1V2", "ETH_VDD33A", "ETH_VDD12A", "ETH_VDD12USB", "ETH_VDD12PLL"):
    k.C(et, g, "10u", ag, fp=C0805)
for ag in ("ETH_VDD33A", "ETH_VDD12A", "ETH_VDD12USB", "ETH_VDD12PLL"):
    k.bayrak(et, g, ag)

et.metin("HAT: her uca 49,9 ohm yukari cekme (3,3 V); trafonun entegre tarafi orta uclari ayni 3,3 V'a; kablo tarafi 75 ohm + 1 nF.", 30, 300)
g = Izgara(50, 335, sutun=16)
for c in "ABCD":
    k.R(et, g, "49R9 1%", "+3V3", "MDI_%s+" % c); k.R(et, g, "49R9 1%", "+3V3", "MDI_%s-" % c)
tr = {}
for c, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
    tr.update({str(cp): "MDI_%s+" % c, str(cm): "MDI_%s-" % c, str(cc): "+3V3", str(kp_): "ETH_%s+" % c, str(km_): "ETH_%s-" % c, str(kc_): "KCT_%s" % c})
k.koy(et, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", 110, 420, tr, "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13")
g = Izgara(190, 410, sutun=10)
for c in "ABCD":
    k.R(et, g, "75R", "KCT_%s" % c, "ETH_BS")
k.C(et, g, "1n 2kV", "ETH_BS", fp=C1206)
et.yaz(os.path.join(BURASI, "ethernet.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_pc_adaptor.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, ub, et], {"operfly": ORTAK_URI})
print("elemanlar:", dict(sorted(k.sayac.items())))
