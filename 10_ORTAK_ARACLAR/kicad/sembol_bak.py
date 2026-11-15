"""KiCad standart kütüphanesindeki sembollerin pinlerini listeler.

Kullanım: python sembol_bak.py Kutuphane:Sembol [Kutuphane:Sembol ...]
"""
import os
import re
import sys

from pin_cikar import blok, sembol_blogu
from sema_uret import kicad_sembol_dizini


def main():
    d = kicad_sembol_dizini()
    for tam in sys.argv[1:]:
        lib, ad = tam.split(":", 1)
        metin = open(os.path.join(d, lib + ".kicad_sym"), encoding="utf-8").read()
        b, temel = sembol_blogu(metin, ad)
        fp = re.search(r'\(property "Footprint" "([^"]*)"', b)
        if temel:
            b, _ = sembol_blogu(metin, temel)
        birim = sorted(set(re.findall(r'\(symbol "%s_(\d+)_\d+"' % re.escape(temel or ad), b)))
        print("== %s%s | ayak izi: %s | birimler: %s" % (tam, " (temel: %s)" % temel if temel else "", fp.group(1) if fp else "", ",".join(birim)))
        for m in re.finditer(r"\(pin (\w+) (\w+)", b):
            p = blok(b, m.start())
            at = re.search(r"\(at ([-\d.]+) ([-\d.]+) (\d+)\)", p)
            print("   %-4s %-14s %-14s (%s, %s, %s)" % (re.search(r'\(number "([^"]*)"', p).group(1), re.search(r'\(name "([^"]*)"', p).group(1), m.group(1), at.group(1), at.group(2), at.group(3)))


if __name__ == "__main__":
    main()
