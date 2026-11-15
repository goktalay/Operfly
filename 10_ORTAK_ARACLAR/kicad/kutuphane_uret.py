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


def main():
    s = '(kicad_symbol_lib (version 20231120) (generator "operfly") (generator_version "1")\n'
    s += konnektor("Operfly_Bus_20", BUS, FP_BUS, "Operfly Bus portu, Harwin Gecko-SL 20 kontak")
    s += ")\n"
    open(sys.argv[1], "w", encoding="utf-8", newline="\n").write(s)
    print("yazıldı:", sys.argv[1])


if __name__ == "__main__":
    main()
