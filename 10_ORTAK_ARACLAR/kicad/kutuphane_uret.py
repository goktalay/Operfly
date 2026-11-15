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


def kutu(ad, sol, sag, ust, alt, fp, aciklama, yari=10.16):
    """Dikdörtgen entegre sembolü. Her uç: (numara, ad, tür). sol/sag yan uçlar, ust besleme, alt toprak."""
    n = max(len(sol), len(sag), 1)
    y0 = (n - 1) * 1.27
    tepe = y0 + 2.54
    s = '\t(symbol "%s" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n' % ad
    s += ozellik("Reference", "U", -yari, tepe + 6.35) + ozellik("Value", ad, yari, -tepe - 6.35)
    s += ozellik("Footprint", fp, 0, 0, True) + ozellik("Datasheet", "", 0, 0, True) + ozellik("Description", aciklama, 0, 0, True)
    s += '\t\t(symbol "%s_0_1" (rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.254) (type default)) (fill (type background))))\n' % (ad, -yari, tepe, yari, -tepe)
    s += '\t\t(symbol "%s_1_1"\n' % ad

    def pin(no, isim, tur, x, y, aci):
        return '\t\t\t(pin %s line (at %.2f %.2f %d) (length 2.54) (name "%s" (effects (font (size 1.27 1.27)))) (number "%s" (effects (font (size 1.27 1.27)))))\n' % (tur, x, y, aci, isim, no)
    for i, (no, isim, tur) in enumerate(sol):
        s += pin(no, isim, tur, -yari - 2.54, y0 - i * 2.54, 0)
    for i, (no, isim, tur) in enumerate(sag):
        s += pin(no, isim, tur, yari + 2.54, y0 - i * 2.54, 180)
    for grup, y, aci in ((ust, tepe + 2.54, 270), (alt, -tepe - 2.54, 90)):
        for i, (no, isim, tur) in enumerate(grup):
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


def main():
    s = '(kicad_symbol_lib (version 20231120) (generator "operfly") (generator_version "1")\n'
    s += konnektor("Operfly_Bus_20", BUS, FP_BUS, "Operfly Bus portu, Harwin Gecko-SL 20 kontak")
    for e in ENTEGRELER:
        s += kutu(*e[:7], yari=e[7])
    s += ")\n"
    open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(s)
    print("yazıldı:", sys.argv[1])


if __name__ == "__main__":
    main()
