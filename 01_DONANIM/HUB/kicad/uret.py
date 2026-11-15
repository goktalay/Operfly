"""Operfly Hub şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py HUB operfly_hub`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Bu sürümde güç dağıtımı çizilidir (12 port, port başına elektronik sigorta ve akım ölçümü). Ethernet anahtarı
ayrı sayfadır ve henüz çizilmemiştir; portların Ethernet uçları şimdilik bağlı değildir.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, ORTAK_URI, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
PORT = 12
k = Kart("operfly_hub", "2026-11-15")
kok = Sema(k.P, "Operfly Hub", kagit="A3", tarih=k.T)
kok.metin("Operfly Hub - omurga merkezi (OPFHUB)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/HUB/kicad/uret.py. Ethernet: uc adet KSZ9567R, her biri dort porta hizmet eder.", 25.4, 33.02, 1.6)

EK = {"PA0": "IMON_MUX", "PA1": "V12_SENS",                               # ADC1_IN0, ADC1_IN1
      "PA4": "MUX_S0", "PA5": "MUX_S1", "PA6": "MUX_S2", "PA7": "MUX_S3",
      "PB10": "HUB_SCL", "PB11": "HUB_SDA", "PB0": "EXP_INT_N",           # I2C2
      "PB3": "SW_SCK", "PB4": "SW_MISO", "PA2": "SW_MOSI",                # SPI1: Ethernet anahtarlarinin yonetimi
      "PB6": "SW_CS_A", "PB7": "SW_CS_B", "PC6": "SW_CS_C", "PC7": "SW_RESET_N"}
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, port=False, sonlandirma=True)

# --- Guc girisi ve ortak denetim ----------------------------------------------
gc = Sema(k.P, "Operfly Hub - guc girisi, port denetimi ve akim olcumu", kagit="A1", tarih=k.T, ust=kok, ad="Guc", genel_etiket=True)
kok.alt_sayfa(gc, "guc.kicad_sch", 101.6, 50.8)
gc.metin("12 V GIRIS (Power kartindan, XT60). Dugum devresi 2 A sigortayla ayni hattan beslenir.", 30, 30)
g = Izgara(50, 65, sutun=14)
x, y = g.yer()
k.koy(gc, "Connector_Generic:Conn_01x02", "J", "12 V giris (XT60)", x + 5, y, {"Pin_1": "+12V_HUB", "Pin_2": "GND"}, "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical")
k.iki(gc, g, "Device:D_TVS", "D", "SMBJ18A", "+12V_HUB", "GND", "Diode_SMD:D_SMB")
k.iki(gc, g, "Device:C_Polarized", "C", "330u 25V", "+12V_HUB", "GND", "Capacitor_SMD:CP_Elec_8x10")
k.iki(gc, g, "Device:C_Polarized", "C", "330u 25V", "+12V_HUB", "GND", "Capacitor_SMD:CP_Elec_8x10")
k.iki(gc, g, "Device:Polyfuse", "F", "2 A (kendini onaran)", "+12V_HUB", "+12V_BUS", "Fuse:Fuse_1812_4532Metric")
k.R(gc, g, "47k 1%", "+12V_HUB", "V12_SENS"); k.R(gc, g, "10k 1%", "V12_SENS", "GND"); k.C(gc, g, "100n", "V12_SENS")
k.bayrak(gc, g, "+12V_HUB")

gc.metin("ORTAK ESIKLER: portlar giris 9,6 V'u gecince acilir (9,0 V altinda kapanir); 15 V ustunde kapanir.", 30, 115)
g = Izgara(50, 145, sutun=14)
k.R(gc, g, "100k 1%", "+12V_HUB", "HUB_UVLO"); k.R(gc, g, "14k3 1%", "HUB_UVLO", "GND")
k.R(gc, g, "100k 1%", "+12V_HUB", "HUB_OVP"); k.R(gc, g, "8k66 1%", "HUB_OVP", "GND")

gc.metin("PORT DENETIMI: 1. genisletici portlari acar/kapatir (adres 0x20), 2. genisletici ariza girislerini okur (adres 0x21).", 30, 195)
gc.metin("AKIM OLCUMU: 12 portun akim cikisi tek bir analog seciciyle isleme alinir (6 A = 3,0 V).", 30, 201)
en = {"IO%d_%d" % (n // 8, n % 8): "P%d_EN" % (n + 1) for n in range(PORT)}
fl = {"IO%d_%d" % (n // 8, n % 8): "P%d_FLT_N" % (n + 1) for n in range(PORT)}
ortak = {"VDD": "+3V3", "VSS": "GND", "SCL": "HUB_SCL", "SDA": "HUB_SDA", "A1": "GND", "A2": "GND"}
k.koy(gc, "Interface_Expansion:PCA9555PW", "U", "PCA9555PW", 90, 270, dict(en, A0="GND", **ortak), "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm")
k.koy(gc, "Interface_Expansion:PCA9555PW", "U", "PCA9555PW", 220, 270, dict(fl, A0="+3V3", **{"~{INT}": "EXP_INT_N"}, **ortak), "Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm")
mux = {"I%d" % n: ("P%d_IMON" % (n + 1) if n < PORT else "GND") for n in range(16)}
mux.update({"COM": "IMON_MUX", "S0": "MUX_S0", "S1": "MUX_S1", "S2": "MUX_S2", "S3": "MUX_S3", "~{E}": "GND", "VCC": "+3V3", "GND": "GND"})
k.koy(gc, "74xx:CD74HC4067SM", "U", "CD74HC4067SM96", 360, 270, mux, "Package_SO:SSOP-24_5.3x8.2mm_P0.65mm")
g = Izgara(440, 240, sutun=8)
k.R(gc, g, "2k2", "+3V3", "HUB_SCL"); k.R(gc, g, "2k2", "+3V3", "HUB_SDA"); k.R(gc, g, "10k", "+3V3", "EXP_INT_N")
for _ in range(3):
    k.C(gc, g, "100n", "+3V3")
k.C(gc, g, "100n", "IMON_MUX")
gc.yaz(os.path.join(BURASI, "guc.kicad_sch"))

# --- Portlar: 12 omurga portu, her birinde elektronik sigorta -----------------
pt = Sema(k.P, "Operfly Hub - 12 omurga portu ve port sigortalari", kagit="A0", tarih=k.T, ust=kok, ad="Portlar", genel_etiket=True)
kok.alt_sayfa(pt, "portlar.kicad_sch", 177.8, 50.8)
pt.metin("Her portta TPS26630: akim siniri 6 A (3k01), yumusak acilis ~11 ms (47 nF), asiri akimda kendiliginden yeniden dener.", 30, 25)
pt.metin("CAN A/B ve PPS tum portlarda ortaktir. Ethernet ciftleri anahtar sayfalarindaki trafolara gider.", 30, 31)
for n in range(1, PORT + 1):
    x0, y0 = 30 + ((n - 1) % 4) * 285, 50 + ((n - 1) // 4) * 255
    p = "P%d" % n
    pt.metin("PORT %d" % n, x0, y0, 2.5)
    eth = {"ETH_%s%s" % (c, i): "%s_ETH_%s%s" % (p, c, i) for c in "ABCD" for i in "+-"}
    k.koy(pt, "operfly:Operfly_Bus_20", "J", "Port %d" % n, x0 + 35, y0 + 60, dict(eth, **{"+12V": p + "_12V", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L",
          "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L", "PPS": "PPS_BUS"}), "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical")
    k.koy(pt, "Power_Management:TPS26630RGE", "U", "TPS26630RGER", x0 + 120, y0 + 60, {
        "IN": "+12V_HUB", "IN_SYS": "+12V_HUB", "UVLO": "HUB_UVLO", "OVP": "HUB_OVP", "GND": "GND", "MODE": "GND",
        "dVdT": p + "_DVDT", "ILIM": p + "_ILIM", "~{SHDN}": p + "_EN", "IMON": p + "_IMON", "~{FLT}": p + "_FLT_N",
        "PGTH": p + "_PGTH", "OUT": p + "_12V"}, "Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias")
    g = Izgara(x0 + 20, y0 + 135, sutun=10, dx=24)
    k.C(pt, g, "100n 50V", "+12V_HUB", fp=C0603); k.C(pt, g, "1u 25V", p + "_12V", fp=C0603)
    k.R(pt, g, "3k01 1%", p + "_ILIM", "GND"); k.C(pt, g, "47n", p + "_DVDT")
    k.R(pt, g, "18k 1%", p + "_IMON", "GND"); k.C(pt, g, "100n", p + "_IMON")
    k.R(pt, g, "100k", "+3V3", p + "_EN"); k.R(pt, g, "10k", "+3V3", p + "_FLT_N")
    k.R(pt, g, "100k 1%", p + "_12V", p + "_PGTH"); k.R(pt, g, "13k7 1%", p + "_PGTH", "GND")
pt.yaz(os.path.join(BURASI, "portlar.kicad_sch"))

# --- Anahtar beslemeleri: 12 V -> 3,3 V / 2,5 V / 1,2 V (uc adet TPS62130) ------
bs = Sema(k.P, "Operfly Hub - Ethernet anahtari beslemeleri", kagit="A2", tarih=k.T, ust=kok, ad="Anahtar_Besleme", genel_etiket=True)
kok.alt_sayfa(bs, "anahtar_besleme.kicad_sch", 254.0, 50.8)
bs.metin("ANAHTAR BESLEMELERI: uc ayni regulator (TPS62130, 3 A), yalnizca geri besleme direncleri farkli. Cikis = 0,8 V x (1 + Rust/Ralt).", 30, 30)
bs.metin("Anahtarlarin akim tuketimi uretici belgesinden dogrulanacak; 3 A'lik regulatorler pay birakmak icin secildi.", 30, 36)
for i, (ag, rust, ralt, aciklama) in enumerate((("+3V3_SW", "316k 1%", "100k 1%", "3,3 V (giris/cikis uclari)"),
                                                ("+2V5", "215k 1%", "100k 1%", "2,5 V (analog)"),
                                                ("+1V2", "100k 1%", "200k 1%", "1,2 V (cekirdek)"))):
    bs.metin(aciklama, 30, 62 + i * 90)
    g = Izgara(50, 95 + i * 90, sutun=14)
    n = "REG" + ag.replace("+", "_").replace("V", "V")
    k.parca(bs, g, "Regulator_Switching:TPS62130", "U", "TPS62130RGTR", {"VIN": "+12V_HUB", "EN": "+12V_HUB", "GND": "GND", "SW": n + "_SW", "VOS": ag,
            "FB": n + "_FB", "SS/TR": n + "_SS", "DEF": "GND", "FSW": "GND"}, "Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias", bosluk=2, dx=20)
    k.C(bs, g, "10u 25V", "+12V_HUB", fp="Capacitor_SMD:C_1206_3216Metric"); k.C(bs, g, "100n 25V", "+12V_HUB", fp=C0603)
    k.iki(bs, g, "Device:L", "L", "2u2 XAL4020-222", n + "_SW", ag, "Inductor_SMD:L_Coilcraft_XAL4020-XXX")
    k.C(bs, g, "22u 10V", ag, fp="Capacitor_SMD:C_1206_3216Metric"); k.C(bs, g, "22u 10V", ag, fp="Capacitor_SMD:C_1206_3216Metric")
    k.R(bs, g, rust, ag, n + "_FB"); k.R(bs, g, ralt, n + "_FB", "GND"); k.C(bs, g, "3n3", n + "_SS")
    k.olcum_noktasi(bs, g, ag); k.bayrak(bs, g, ag)
bs.yaz(os.path.join(BURASI, "anahtar_besleme.kicad_sch"))

# --- Ethernet anahtarlari: uc KSZ9567R, her biri dort port; aralarinda RGMII ----
TRAFO = "Transformer_SMD:Transformer_Ethernet_HALO_TG111-MSC13"
anahtar_sayfalari = []
# Zincir: A.port6 <-> B.port6, B.port7 <-> C.port6. A ve C'nin 7. portu kullanilmaz.
BAG = {"A": {6: "AB"}, "B": {6: "BA", 7: "BC"}, "C": {6: "CB"}}
for i, h in enumerate("ABC"):
    sw = Sema(k.P, "Operfly Hub - Ethernet anahtari %s (port %d-%d)" % (h, i * 4 + 1, i * 4 + 4), kagit="A0", tarih=k.T, ust=kok, ad="Anahtar_%s" % h, genel_etiket=True)
    kok.alt_sayfa(sw, "anahtar_%s.kicad_sch" % h.lower(), 25.4 + i * 76.2, 101.6)
    anahtar_sayfalari.append(sw)
    S = "S" + h
    sw.metin("ETHERNET ANAHTARI %s (KSZ9567R): 1-4. bakir portlar omurga portlari %d-%d; 5. bakir port kullanilmaz." % (h, i * 4 + 1, i * 4 + 4), 30, 25)
    sw.metin("Yonetim SPI ile dugum islemcisinden. Acilista anahtar KAPALI baslar (LED5_1 asagi cekili): islemci izin verene kadar veri gecmez.", 30, 31)
    ag = {"AVDDH": S + "_AVDDH", "AVDDL": S + "_AVDDL", "DVDDL": "+1V2", "VDDIO": "+3V3_SW", "GND": "GND", "EP": "GND",
          "RESET_N": "SW_RESET_N", "SCS_N": "SW_CS_" + h, "SCL": "SW_SCK", "SDI": "SW_MOSI", "SDO": "SW_MISO",
          "XI": S + "_XI", "XO": S + "_XO", "ISET": S + "_ISET", "LED5_1": S + "_START"}
    for kp in (1, 2, 3, 4):
        for c in "ABCD":
            ag["TXRX%dP_%s" % (kp, c)] = "P%d_MDI_%s+" % (i * 4 + kp, c)
            ag["TXRX%dM_%s" % (kp, c)] = "P%d_MDI_%s-" % (i * 4 + kp, c)
    for port, yon in BAG[h].items():
        gelen, giden = "RG_%s%s" % (yon[1], yon[0]), "RG_%s" % yon          # ornek: A icin giden RG_AB, gelen RG_BA
        ag.update({"TX_CLK%d" % port: gelen + "_CLK", "TX_CTL%d" % port: gelen + "_CTL", "RX_CLK%d" % port: giden + "_CLK", "RX_CTL%d" % port: giden + "_CTL"})
        for b in range(4):
            ag["TXD%d_%d" % (port, b)] = "%s_D%d" % (gelen, b); ag["RXD%d_%d" % (port, b)] = "%s_D%d" % (giden, b)
    k.koy(sw, "operfly:KSZ9567R", "U", "KSZ9567RTXI", 150, 300, ag, "operfly_ayak:Microchip_TQFP-128-1EP_14x14mm_P0.4mm_EP10x10mm")

    sw.metin("TRAFOLAR (1000BASE-T, 4 cift): entegre tarafi orta uclari ayri ayri 100 nF ile topraga; kablo tarafi 75 ohm + 1 nF.", 330, 60)
    for kp in (1, 2, 3, 4):
        n = i * 4 + kp
        y0 = 110 + (kp - 1) * 110
        tr = {}
        for c, (cp, cm, cc), (kp_, km_, kc_) in zip("ABCD", ((2, 3, 1), (5, 6, 4), (8, 9, 7), (11, 12, 10)), ((23, 22, 24), (20, 19, 21), (17, 16, 18), (14, 13, 15))):
            tr.update({str(cp): "P%d_MDI_%s+" % (n, c), str(cm): "P%d_MDI_%s-" % (n, c), str(cc): "P%d_CT_%s" % (n, c),
                       str(kp_): "P%d_ETH_%s+" % (n, c), str(km_): "P%d_ETH_%s-" % (n, c), str(kc_): "P%d_KCT_%s" % (n, c)})
        k.koy(sw, "Transformer:TG111-MSC13LF", "T", "TG111-MSC13LF", 380, y0, tr, TRAFO)
        g = Izgara(450, y0 - 15, sutun=9, dx=24)
        for c in "ABCD":
            k.C(sw, g, "100n", "P%d_CT_%s" % (n, c))
        for c in "ABCD":
            k.R(sw, g, "75R", "P%d_KCT_%s" % (n, c), "P%d_BS" % n)
        k.C(sw, g, "1n 2kV", "P%d_BS" % n, fp="Capacitor_SMD:C_1206_3216Metric")

    sw.metin("SAAT, AYAR ve BESLEME SUZGECLERI: 25 MHz kristal, ISET 6k04, analog beslemeler ferrit uzerinden, her besleme ucuna 100 nF.", 330, 560)
    g = Izgara(340, 600, sutun=20, dx=24)
    k.koy(sw, "Device:Crystal_GND24", "Y", "25 MHz 50 ppm", *g.yer(), {"1": S + "_XI", "3": S + "_XO", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
    k.C(sw, g, "12p", S + "_XI"); k.C(sw, g, "12p", S + "_XO")
    k.R(sw, g, "6k04 1%", S + "_ISET", "GND"); k.R(sw, g, "1k", S + "_START", "GND")
    k.iki(sw, g, "Device:FerriteBead", "FB", "BLM18PG221", "+2V5", S + "_AVDDH", "Inductor_SMD:L_0603_1608Metric")
    k.iki(sw, g, "Device:FerriteBead", "FB", "BLM18PG221", "+1V2", S + "_AVDDL", "Inductor_SMD:L_0603_1608Metric")
    k.C(sw, g, "10u", S + "_AVDDH", fp="Capacitor_SMD:C_0805_2012Metric"); k.C(sw, g, "10u", S + "_AVDDL", fp="Capacitor_SMD:C_0805_2012Metric")
    k.C(sw, g, "10u", "+1V2", fp="Capacitor_SMD:C_0805_2012Metric"); k.C(sw, g, "10u", "+3V3_SW", fp="Capacitor_SMD:C_0805_2012Metric")
    k.bayrak(sw, g, S + "_AVDDH"); k.bayrak(sw, g, S + "_AVDDL")
    g.satir()
    for besleme, adet in ((S + "_AVDDH", 7), (S + "_AVDDL", 9), ("+1V2", 8), ("+3V3_SW", 3)):
        for _ in range(adet):
            k.C(sw, g, "100n", besleme)
    if h == "A":   # ortak yonetim hatlari bir kez
        g.satir()
        k.R(sw, g, "4k7", "+3V3_SW", "SW_MOSI"); k.R(sw, g, "10k", "SW_RESET_N", "GND")
        for cs in "ABC":
            k.R(sw, g, "10k", "+3V3_SW", "SW_CS_" + cs)
    sw.yaz(os.path.join(BURASI, "anahtar_%s.kicad_sch" % h.lower()))

kok.yaz(os.path.join(BURASI, "operfly_hub.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, gc, pt, bs] + anahtar_sayfalari, {"operfly": ORTAK_URI, "operfly_ayak": "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"})
print("elemanlar:", dict(sorted(k.sayac.items())))
