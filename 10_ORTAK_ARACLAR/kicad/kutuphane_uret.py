"""Operfly ortak sembol kütüphanesini üretir (01_DONANIM/ORTAK_KUTUPHANE/semboller/operfly.kicad_sym).

Kullanım: python kutuphane_uret.py <cikti.kicad_sym>
Üretilen dosya eski biçim sürümüyle yazılır; ardından `kicad-cli sym upgrade` ile güncel biçime çevrilir.
"""
import sys

# Operfly Bus, 20 kontak. Sütun düzeni: pin n ile pin n+10 karşı karşıyadır.
BUS = ["+12V", "+12V", "GND", "CAN_A_H", "CAN_B_H", "PPS", "ETH_A+", "ETH_B+", "ETH_C+", "ETH_D+",
       "+12V", "GND", "GND", "CAN_A_L", "CAN_B_L", "GND", "ETH_A-", "ETH_B-", "ETH_C-", "ETH_D-"]
FP_BUS = "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical"


def ozellik(ad, deger, x, y, gizli=False):
    g = " (hide yes)" if gizli else ""
    return '\t\t(property "%s" "%s" (at %s %s 0) (effects (font (size 1.27 1.27))%s))\n' % (ad, deger, x, y, g)


def konnektor(ad, pinler, fp, aciklama):
    n = len(pinler) // 2
    ust = (n - 1) * 1.27
    s = '\t(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n' % ad
    s += ozellik("Reference", "J", 0, ust + 5.08) + ozellik("Value", ad, 0, -ust - 5.08)
    s += ozellik("Footprint", fp, 0, 0, True) + ozellik("Datasheet", "", 0, 0, True) + ozellik("Description", aciklama, 0, 0, True)
    s += '\t\t(symbol "%s_0_1" (rectangle (start -10.16 %.2f) (end 10.16 %.2f) (stroke (width 0.254) (type default)) (fill (type background))))\n' % (ad, ust + 2.54, -ust - 2.54)
    s += '\t\t(symbol "%s_1_1"\n' % ad
    for i, p in enumerate(pinler):
        sol = i < n
        y = ust - (i % n) * 2.54
        s += '\t\t\t(pin passive line (at %s %.2f %d) (length 2.54) (name "%s" (effects (font (size 1.27 1.27)))) (number "%d" (effects (font (size 1.27 1.27)))))\n' % (
            "-12.7" if sol else "12.7", y, 0 if sol else 180, p, i + 1)
    return s + "\t\t)\n\t)\n"


def kutu(ad, sol, sag, ust, alt, fp, aciklama, yari=10.16, yigin=False):
    """Dikdörtgen entegre sembolü. Her uç: (numara, ad, tür). sol/sag yan uçlar, ust besleme, alt toprak.

    yigin=True: üstte ve altta aynı adı taşıyan uçlar aynı noktada üst üste durur (ilki görünür, diğerleri gizli).
    """
    n = max(len(sol), len(sag), 1)
    y0 = (n - 1) * 1.27
    tepe = y0 + 2.54
    s = '\t(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n' % ad
    s += ozellik("Reference", "U", -yari, tepe + 6.35) + ozellik("Value", ad, yari, -tepe - 6.35)
    s += ozellik("Footprint", fp, 0, 0, True) + ozellik("Datasheet", "", 0, 0, True) + ozellik("Description", aciklama, 0, 0, True)
    s += '\t\t(symbol "%s_0_1" (rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) (fill (type background))))\n' % (ad, -yari, tepe, yari, -tepe)
    s += '\t\t(symbol "%s_1_1"\n' % ad

    def pin(no, isim, tur, x, y, aci, gizli=False):
        return '\t\t\t(pin %s line (at %.2f %.2f %d) (length 2.54)%s (name "%s" (effects (font (size 1.27 1.27)))) (number "%s" (effects (font (size 1.27 1.27)))))\n' % (
            "passive" if gizli else tur, x, y, aci, " hide" if gizli else "", isim, no)
    for i, (no, isim, tur) in enumerate(sol):
        s += pin(no, isim, tur, -yari - 2.54, y0 - i * 2.54, 0)
    for i, (no, isim, tur) in enumerate(sag):
        s += pin(no, isim, tur, yari + 2.54, y0 - i * 2.54, 180)
    for grup, y, aci in ((ust, tepe + 2.54, 270), (alt, -tepe - 2.54, 90)):
        adlar = list(dict.fromkeys(u[1] for u in grup)) if yigin else None
        gorulen = set()
        for i, (no, isim, tur) in enumerate(grup):
            if yigin:
                s += pin(no, isim, tur, (adlar.index(isim) - (len(adlar) - 1) / 2) * 5.08, y, aci, gizli=isim in gorulen)
                gorulen.add(isim)
            else:
                s += pin(no, isim, tur, (i - (len(grup) - 1) / 2) * 5.08, y, aci)
    return s + "\t\t)\n\t)\n"


I, O, B, P, G, V, N = "input", "output", "bidirectional", "passive", "power_in", "power_out", "no_connect"
LGA14 = "Package_LGA:Bosch_LGA-14_3x2.5mm_P0.5mm"

# Uç sıraları üretici belgelerinden; kart çizimine geçmeden ayak iziyle birlikte bir kez daha doğrulanır.
ENTEGRELER = [
    ("ICM-42688-P",
     [("12", "AP_CS", I), ("13", "AP_SCLK", I), ("14", "AP_SDI", B), ("1", "AP_SDO", B)],
     [("4", "INT1", O), ("9", "INT2/FSYNC/CLKIN", B), ("2", "RESV2", P), ("3", "RESV3", P), ("7", "RESV7", P), ("10", "RESV10", P), ("11", "RESV11", P)],
     [("8", "VDD", G), ("5", "VDDIO", G)], [("6", "GND", G)], LGA14, "6 eksen IMU, TDK InvenSense, LGA-14 2,5x3 mm", 12.7),
    ("ICM-45686",
     [("12", "AP_CS", I), ("13", "AP_SCLK", I), ("14", "AP_SDI", B), ("1", "AP_SDO", B)],
     [("4", "INT1", O), ("9", "INT2/FSYNC/CLKIN", B), ("2", "RESV2", P), ("3", "RESV3", P), ("7", "RESV7", P), ("10", "RESV10", P), ("11", "RESV11", P)],
     [("8", "VDD", G), ("5", "VDDIO", G)], [("6", "GND", G)], LGA14, "6 eksen IMU, TDK InvenSense, LGA-14 2,5x3 mm", 12.7),
    ("BMP390",
     [("2", "SCK", I), ("4", "SDI", B), ("5", "SDO", P), ("6", "CSB", I)],
     [("7", "INT", O)],
     [("10", "VDD", G), ("1", "VDDIO", G)], [("3", "VSS", G), ("8", "VSS", G), ("9", "VSS", G)],
     "Package_LGA:ST_HLGA-10_2x2mm_P0.5mm_LayoutBorder3x2y", "Barometre, Bosch, LGA-10 2x2 mm (ayak izi gecici, uretici cizimiyle dogrulanacak)", 10.16),
    ("SE050",
     [("9", "I2C_SDA", B), ("10", "I2C_SCL", I), ("11", "ENA", I)],
     [("3", "IO1", P), ("16", "IO2", P), ("13", "CLK", P), ("14", "RST_N", P), ("17", "LA", P), ("1", "LB", P),
      ("2", "NC", N), ("4", "NC", N), ("5", "NC", N), ("6", "NC", N), ("7", "NC", N), ("8", "NC", N), ("20", "NC", N)],
     [("12", "VIN", G), ("18", "VCC", G), ("15", "VOUT", V)], [("19", "VSS", G), ("21", "EP", P)],
     "Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm", "Guvenli eleman, NXP EdgeLock SE050, HX2QFN20 (ayak izi gecici, uretici cizimiyle dogrulanacak)", 10.16),
]


def ksz9567r():
    """KSZ9567R, 128 uclu TQFP + alt ped. Uc numaralari uretici belgesindeki pin atama tablosundan (Tablo 3-1)."""
    T = "tri_state"
    sol, no = [], {1: (1, 4, 6, 8), 2: (12, 15, 17, 20), 3: (24, 26, 28, 31), 4: (34, 37, 39, 42), 5: (112, 115, 117, 120)}
    for port in (1, 2, 3, 4, 5):
        for cift, n in zip("ABCD", no[port]):
            sol += [(str(n), "TXRX%dP_%s" % (port, cift), B), (str(n + 1), "TXRX%dM_%s" % (port, cift), B)]
    sag = []
    for port, t in ((6, 48), (7, 66)):
        sag += [(str(t), "TX_CLK%d" % port, I), (str(t + 1), "TX_CTL%d" % port, I), (str(t + 2), "TX_ER%d" % port, P), (str(t + 3), "COL%d" % port, P)]
        sag += [(str(t + 4 + i), "TXD%d_%d" % (port, 3 - i), I) for i in range(4)]
    sag += [("57", "RX_CLK6", O), ("58", "RX_CTL6", O), ("59", "RX_ER6", P), ("60", "CRS6", P)] + [(str(62 + i), "RXD6_%d" % (3 - i), B) for i in range(4)]
    sag += [("75", "RX_CLK7", O), ("76", "RX_CTL7", B), ("78", "RX_ER7", P), ("79", "CRS7", P)] + [(str(80 + i), "RXD7_%d" % (3 - i), B) for i in range(4)]
    sag += [("96", "RESET_N", I), ("100", "SCS_N", I), ("101", "SCL", I), ("98", "SDI", B), ("97", "SDO", T), ("94", "INTRP_N", P), ("93", "PME_N", P),
            ("95", "SYNCLKO", O), ("90", "GPIO_1", B), ("105", "LED1_0", B), ("106", "LED1_1", B), ("91", "LED2_0", B), ("92", "LED2_1", B),
            ("88", "LED3_0", B), ("89", "LED3_1", B), ("85", "LED4_0", B), ("86", "LED4_1", B), ("102", "LED5_0", B), ("103", "LED5_1", B),
            ("126", "XI", I), ("125", "XO", O), ("127", "ISET", P), ("108", "NC", N)]
    ust = [(str(n), "AVDDH", G) for n in (10, 22, 33, 44, 111, 122, 128)] + [(str(n), "AVDDL", G) for n in (3, 14, 19, 30, 36, 41, 114, 119, 124)]
    ust += [(str(n), "DVDDL", G) for n in (11, 23, 45, 56, 74, 87, 104, 110)] + [(str(n), "VDDIO", G) for n in (61, 77, 99)]
    alt = [(str(n), "GND", G) for n in (46, 47, 84, 107, 109, 123)] + [("129", "EP", P)]
    assert len(sol) + len(sag) + len(ust) + len(alt) == 129 and len({x[0] for x in sol + sag + ust + alt}) == 129
    return kutu("KSZ9567R", sol, sag, ust, alt, "operfly_ayak:Microchip_TQFP-128-1EP_14x14mm_P0.4mm_EP10x10mm",
                "7 portlu gigabit Ethernet anahtari, 5 bakir port + 2 RGMII, PTP", yari=73.66)


def mosaic():
    """Septentrio mosaic-X5 / mosaic-H (239 uclu LGA). Uc numaralari mosaic_padleri.py tablosundan (uretici belgesi, Ek G).

    Birim 1: islevsel uclar. Cok sayidaki GND, VDD_3V3 ve VANT ucu ayni noktada ust uste durur (ilki gorunur, digerleri gizli).
    Birim 2: ayrilmis (Reserved_NC) uclar; her biri ayri durur ve bos birakilir.
    """
    from mosaic_padleri import PADLER
    T = "tri_state"
    sol = [("nRST_IN", I), ("ONOFF", I), ("MODULE_RDY", O), ("PMIC_ON_REQ", O), None,
           ("TXD1", O), ("RXD1", I), ("RTS1", O), ("CTS1", I), ("TXD2", O), ("RXD2", I), ("RTS2", O), ("CTS2", I),
           ("TXD3", O), ("RXD3", I), ("RTS3", O), ("CTS3", I), ("TXD4", O), ("RXD4", I), None,
           ("PPSO", T), ("EVENTA", I), ("EVENTB", I), ("GP1", T), ("GP2", T), None,
           ("GPLED", T), ("GPLED2", T), ("LOGLED", T), ("LOGBUTTON", I)]
    sag = [("ANT_1", P), ("ANT_2", P), None, ("REF_O", O), ("REF_I", I), ("VTUNE", P), None,
           ("USB_VBUS1", P), ("USB_DEV_P", B), ("USB_DEV_N", B), None,
           ("SD1_CLK", O), ("SD1_CMD", B), ("SD1_DATA0", B), None,
           ("RMII_CLK", O), ("MDC", O), ("MDIO", B), ("RMII_TXEN", O), ("RMII_TXD0", O), ("RMII_TXD1", O),
           ("RMII_RXD0", I), ("RMII_RXD1", I), ("RMII_CRSDV", I), ("RMII_RXER", I), ("nRST_LAN", O), None,
           ("RTC_XTALI", P), ("RTC_XTALO", P)]
    ust = [("VDD_3V3", G), ("VDD_BAT", G), ("VANT", G), ("2V8_IN", G), ("2V8_OUT", V), ("1V8_OUT", V), ("SYNC", I)]
    alt = [("GND", G), ("Reserved_GND", P)]
    sol, sag = [None] * 5 + sol + [None] * 6, [None] * 5 + sag + [None] * 6   # ust ve alt uc adlarina yer
    ad, yari = "mosaic-X5", 22.86
    n = max(len(sol), len(sag))
    y0 = (n - 1) * 1.27
    tepe = y0 + 2.54
    kullanilan = set()

    def pin(isim, tur, x, y, aci):
        r = ""
        for i, no in enumerate(PADLER[isim]):
            kullanilan.add(no)
            r += '\t\t\t(pin %s line (at %.2f %.2f %d) (length 2.54)%s (name "%s" (effects (font (size 1.27 1.27)))) (number "%s" (effects (font (size 1.27 1.27)))))\n' % (
                tur if i == 0 else "passive", x, y, aci, "" if i == 0 else " hide", isim, no)
        return r
    s = '\t(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n' % ad
    s += ozellik("Reference", "U", -yari, tepe + 6.35) + ozellik("Value", ad, yari, -tepe - 6.35)
    s += ozellik("Footprint", "operfly_ayak:Septentrio_mosaic_LGA-239_31x31mm_P1.27mm", 0, 0, True) + ozellik("Datasheet", "", 0, 0, True)
    s += ozellik("Description", "GNSS alici modulu, Septentrio mosaic-X5 (tek anten) / mosaic-H (cift anten), LGA-239 31x31 mm", 0, 0, True)
    s += '\t\t(symbol "%s_1_1" (rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) (fill (type background)))\n' % (ad, -yari, tepe, yari, -tepe)
    for grup, x, aci in ((sol, -yari - 2.54, 0), (sag, yari + 2.54, 180)):
        for i, u in enumerate(grup):
            if u:
                s += pin(u[0], u[1], x, y0 - i * 2.54, aci)
    for grup, y, aci in ((ust, tepe + 2.54, 270), (alt, -tepe - 2.54, 90)):
        for i, (isim, tur) in enumerate(grup):
            s += pin(isim, tur, (i - (len(grup) - 1) / 2) * 5.08, y, aci)
    s += "\t\t)\n"
    # Birim 2: ayrilmis uclar, iki sutun
    nc = PADLER["Reserved_NC"]
    yarim = (len(nc) + 1) // 2
    t2 = (yarim - 1) * 1.27 + 2.54
    s += '\t\t(symbol "%s_2_1" (rectangle (start -17.78 %.2f) (end 17.78 %.2f) (stroke (width 0.254) (type default)) (fill (type background)))\n' % (ad, t2, -t2)
    for i, no in enumerate(nc):
        kullanilan.add(no)
        solda = i < yarim
        s += '\t\t\t(pin no_connect line (at %s %.2f %d) (length 2.54) (name "Reserved_NC" (effects (font (size 1.27 1.27)))) (number "%s" (effects (font (size 1.27 1.27)))))\n' % (
            "-20.32" if solda else "20.32", (yarim - 1) * 1.27 - (i % yarim) * 2.54, 0 if solda else 180, no)
    assert len(kullanilan) == 239, len(kullanilan)
    return s + "\t\t)\n\t)\n"


def rfd900ux_smt():
    """RFDesign RFD900ux-SMT / RFD868ux-SMT (28 kenar pedi + 2 isi pedi). Uc sirasi uretici veri sayfasindan (V1.3, Tablo 4-3;
    isi pedleri 29 ve 30: Sekil 5-2)."""
    sol = [("25", "RX", I), ("26", "TX", O), ("27", "RTS", O), ("28", "CTS", I), ("4", "SWO", B),
           ("21", "GPIO0", B), ("22", "GPIO1/PPM", B), ("23", "GPIO2", B), ("24", "GPIO3", B)]
    sag = [("13", "ANT1", P), ("16", "ANT2", P), ("10", "+3V3_OUT", V), ("1", "VUSB", P), ("2", "USB_DM", B), ("3", "USB_DP", B),
           ("5", "P3.3", B), ("6", "P3.4", B), ("7", "P3.5", B)]
    ust = [("19", "+5V", G)]
    alt = [(str(n), "GND", G) for n in (8, 9, 11, 12, 14, 15, 17, 18, 20, 29, 30)]
    assert len({u[0] for u in sol + sag + ust + alt}) == 30
    return kutu("RFD900ux-SMT", sol, sag, ust, alt, "operfly_ayak:RFDesign_RFD900ux-SMT",
                "Kumanda radyo modulu, RFDesign RFD900ux-SMT / RFD868ux-SMT, 1 W, frekans atlamali, 21x29 mm", yari=15.24, yigin=True)


def pmddl():
    """Microhard pMDDL2450 OEM (80 kenar pedi + alt toprak duzlemi). Uc sirasi uretici isletme kilavuzundan
    (pMDDL Operating Manual v1.4.2, Cizim 3-5 ve Tablo 3-3). Alt toprak duzlemi kilavuzda numarasizdir; burada 81."""
    sol = [("28", "Serial_RxD", I), ("29", "Serial_TxD", O), ("34", "Serial_RTS", I), ("31", "Serial_CTS", O), ("30", "Serial_DSR", O), ("32", "Serial_DTR", O),
           ("16", "RESET", I), ("15", "CONFIG", I), ("14", "USB_MODE", I), ("18", "USBDP", B), ("19", "USBDM", B),
           ("11", "CPU_STATUS_LED", O), ("20", "RSSI_LED1", O), ("21", "RSSI_LED2", O), ("22", "RSSI_LED3", O), ("23", "LED_RX", O), ("24", "LED_TX", O),
           ("60", "ETH0_LINK_LED", O), ("49", "ETH4_LINK_LED", O)]
    sag = [("55", "TX_P0", P), ("56", "TX_N0", P), ("58", "RX_P0", P), ("57", "RX_N0", P), ("13", "ETH_BIAS", P),
           ("44", "TX_P4", P), ("43", "TX_N4", P), ("42", "RX_P4", P), ("41", "RX_N4", P)]
    sag += [(str(n), "DNC", N) for n in (2, 3, 4, 5, 6)]
    sag += [(str(n), "NC", N) for n in (7, 8, 9, 10, 12, 27, 33, 35, 36, 37, 38, 45, 46, 47, 48, 50, 51, 52, 53, 54, 59)]
    ust = [("61", "Vcc", G), ("62", "Vcc", G), ("63", "VRF", G), ("64", "VRF", G)]
    alt = [(str(n), "GND", G) for n in [1, 17, 25, 26, 39, 40] + list(range(65, 81)) + [81]]
    assert len({u[0] for u in sol + sag + ust + alt}) == 81
    return kutu("pMDDL2450", sol, sag, ust, alt, "operfly_ayak:Microhard_pMDDL_OEM",
                "Genis bant radyo modulu, Microhard pMDDL2450 OEM, 2,4 GHz 2x2 MIMO, 1 W, 26,5x33 mm", yari=20.32, yigin=True)


def jetson():
    """NVIDIA Jetson Orin NX / Orin Nano soketi (260 uclu SO-DIMM). Uc tablosu jetson_uclari.py (uretici veri sayfasi).

    Dort birim: 1 guc ve denetim (GND ve VDD_IN uclari ust uste), 2 PCIe / Ethernet / USB, 3 dusuk hizli giris-cikislar,
    4 bu ekosistemde kullanilmayan goruntu uclari (CSI, DSI, DP). Besleme disindaki uclar pasif tanimlidir.
    """
    from jetson_uclari import UCLAR
    ad = "Jetson_Orin_NX"
    denetim = ("POWER_EN", "SYS_RESET*", "SHUTDOWN_REQ*", "FORCE_RECOVERY*", "MOD_SLEEP*", "SLEEP/WAKE*", "PMIC_BBAT", "MODULE_ID", "CLK_32K_OUT")
    gruplar = {1: [], 2: [], 3: [], 4: []}
    gnd, vdd = [], []
    for no in sorted(UCLAR):
        isim = UCLAR[no]
        if isim == "GND":
            gnd.append(no)
        elif isim == "VDD_IN":
            vdd.append(no)
        elif isim in denetim:
            gruplar[1].append((no, isim))
        elif isim.startswith(("PCIE", "GBE_", "USB")):
            gruplar[2].append((no, isim))
        elif isim.startswith(("CSI", "DSI", "DP", "HDMI", "CAM0", "CAM1")):
            gruplar[4].append((no, isim))
        else:
            gruplar[3].append((no, isim))
    assert len(gnd) + len(vdd) + sum(len(g) for g in gruplar.values()) == 260

    def pin(no, isim, tur, x, y, aci, gizli=False):
        return '\t\t\t(pin %s line (at %.2f %.2f %d) (length 2.54)%s (name "%s" (effects (font (size 1.27 1.27)))) (number "%d" (effects (font (size 1.27 1.27)))))\n' % (
            tur, x, y, aci, " hide" if gizli else "", isim, no)
    s = '\t(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n' % ad
    s += ozellik("Reference", "J", -20.32, 22.86) + ozellik("Value", ad, 20.32, -22.86)
    s += ozellik("Footprint", "Connector_PCBEdge:SODIMM-260_DDR4_H4.0-5.2_OrientationStd_Socket", 0, 0, True) + ozellik("Datasheet", "", 0, 0, True)
    s += ozellik("Description", "NVIDIA Jetson Orin NX / Orin Nano modul soketi, 260 uclu SO-DIMM", 0, 0, True)
    for birim in (1, 2, 3, 4):
        uclar = sorted(gruplar[birim], key=lambda u: (u[1], u[0]))
        yarim = (len(uclar) + 1) // 2
        yari = 30.48 if birim == 1 else 33.02
        tepe = max(yarim - 1, 4) * 1.27 + 5.08
        s += '\t\t(symbol "%s_%d_1" (rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) (fill (type background)))\n' % (ad, birim, -yari, tepe, yari, -tepe)
        for i, (no, isim) in enumerate(uclar):
            solda = i < yarim
            s += pin(no, isim, "passive", -yari - 2.54 if solda else yari + 2.54, (yarim - 1) * 1.27 - (i % yarim) * 2.54, 0 if solda else 180)
        if birim == 1:
            for i, no in enumerate(vdd):
                s += pin(no, "VDD_IN", "power_in" if i == 0 else "passive", 0, tepe + 2.54, 270, i > 0)
            for i, no in enumerate(gnd):
                s += pin(no, "GND", "power_in" if i == 0 else "passive", 0, -tepe - 2.54, 90, i > 0)
        s += "\t\t)\n"
    return s + "\t)\n"


def rtl8111h():
    """Realtek RTL8111H-CG (PCIe gigabit Ethernet denetleyici, 32 uclu QFN + alt ped). Uc sirasi uretici veri sayfasindaki
    uc tanim tablolarindan (Rev. 1.2, Tablo 1-8). PCIe ciftleri ve saat uclari pasif tanimlidir: kart bu entegreyi hem
    PCIe kok aygitina hem de kok kipinde calisan bir modeme baglayabilir."""
    sol = [("13", "HSIP", P), ("14", "HSIN", P), ("17", "HSOP", P), ("18", "HSON", P), ("15", "REFCLK_P", P), ("16", "REFCLK_N", P),
           ("19", "PERSTB", I), ("12", "CLKREQB", B), ("21", "LANWAKEB", B), ("20", "ISOLATEB", I),
           ("28", "CKXTAL1", I), ("29", "CKXTAL2", B), ("31", "RSET", P)]
    sag = [("1", "MDIP0", B), ("2", "MDIN0", B), ("4", "MDIP1", B), ("5", "MDIN1", B), ("6", "MDIP2", B), ("7", "MDIN2", B), ("9", "MDIP3", B), ("10", "MDIN3", B),
           ("27", "LED0", O), ("26", "LED1/GPO", B), ("25", "LED2", O), ("24", "REGOUT", V)]
    ust = [("11", "AVDD33", G), ("32", "AVDD33", G), ("23", "VDDREG", G), ("3", "AVDD10", G), ("8", "AVDD10", G), ("30", "AVDD10", G), ("22", "DVDD10", G)]
    alt = [("33", "GND", G)]
    assert len({u[0] for u in sol + sag + ust + alt}) == 33
    return kutu("RTL8111H", sol, sag, ust, alt, "Package_DFN_QFN:QFN-32-1EP_4x4mm_P0.4mm_EP2.9x2.9mm_ThermalVias",
                "PCIe gigabit Ethernet denetleyici, Realtek RTL8111H-CG, QFN-32 4x4 mm (alt ped olcusu uretici cizimiyle dogrulanacak)", yari=12.7, yigin=True)


def tps61175():
    """Texas Instruments TPS61175PWP (yukselten regulator, 3 A anahtar, HTSSOP-14 + alt ped). Uc sirasi uretici veri
    sayfasindaki uc tablosundan (SLVS892F, "Pin Functions"). NC ucu (11) uretici geregi topraga baglanir; alt ped 15."""
    sol = [("4", "EN", I), ("6", "SYNC", I), ("10", "FREQ", P), ("5", "SS", P), ("8", "COMP", P)]
    sag = [("1", "SW", P), ("2", "SW", P), ("9", "FB", I), ("11", "NC", P)]
    ust = [("3", "VIN", G)]
    alt = [("7", "AGND", G), ("15", "AGND", G), ("12", "PGND", G), ("13", "PGND", G), ("14", "PGND", G)]
    assert len({u[0] for u in sol + sag + ust + alt}) == 15
    return kutu("TPS61175", sol, sag, ust, alt, "Package_SO:Texas_HTSSOP-14-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.94x3.34mm_ThermalVias",
                "Yukselten regulator, Texas Instruments TPS61175PWP, 2,9-18 V giris, 38 V'a kadar cikis, 3 A anahtar (alt ped olcusu uretici cizimiyle dogrulanacak)", yari=10.16, yigin=True)


def main():
    s = '(kicad_symbol_lib (version 20231120) (generator "operfly") (generator_version "1")\n'
    s += konnektor("Operfly_Bus_20", BUS, FP_BUS, "Operfly Bus portu, Harwin Gecko-SL 20 kontak")
    for e in ENTEGRELER:
        s += kutu(*e[:7], yari=e[7])
    s += ksz9567r()
    s += mosaic()
    s += rfd900ux_smt()
    s += pmddl()
    s += jetson()
    s += rtl8111h()
    s += tps61175()
    s += ")\n"
    open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(s)
    print("yazıldı:", sys.argv[1])


if __name__ == "__main__":
    main()
