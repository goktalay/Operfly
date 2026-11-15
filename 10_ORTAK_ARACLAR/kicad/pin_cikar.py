"""KiCad sembol kütüphanesinden bir sembolün pinlerini ve alternatif işlevlerini çıkarır.

Kullanım: python pin_cikar.py <kutuphane.kicad_sym> <sembol_adi> <cikti.json>
"""
import json
import re
import sys


def blok(metin, bas):
    """bas konumundaki '(' ile başlayan dengeli parantez bloğunu döndürür."""
    derinlik = 0
    tirnak = False
    i = bas
    while i < len(metin):
        c = metin[i]
        if c == '"' and metin[i - 1] != "\\":
            tirnak = not tirnak
        elif not tirnak:
            if c == "(":
                derinlik += 1
            elif c == ")":
                derinlik -= 1
                if derinlik == 0:
                    return metin[bas : i + 1]
        i += 1
    raise ValueError("dengesiz parantez")


def sembol_blogu(metin, ad):
    m = re.search(r'\n\t\(symbol "%s"' % re.escape(ad), metin)
    if not m:
        raise SystemExit("sembol bulunamadı: " + ad)
    b = blok(metin, m.start() + 2)
    e = re.search(r'\(extends "([^"]+)"\)', b[:400])
    return (b, e.group(1) if e else None)


def pinler(b):
    sonuc = {}
    for m in re.finditer(r"\(pin (\w+) (\w+)", b):
        p = blok(b, m.start())
        ad = re.search(r'\(name "([^"]*)"', p).group(1)
        no = re.search(r'\(number "([^"]*)"', p).group(1)
        alt = re.findall(r'\(alternate "([^"]*)"', p)
        sonuc.setdefault(ad, {"tur": m.group(1), "numaralar": [], "alternatifler": sorted(set(alt))})
        sonuc[ad]["numaralar"].append(no)
    return sonuc


def main():
    yol, ad, cikti = sys.argv[1:4]
    metin = open(yol, encoding="utf-8").read()
    b, temel = sembol_blogu(metin, ad)
    kaynak = ad
    if temel:
        b, _ = sembol_blogu(metin, temel)
        kaynak = temel
    fp = re.search(r'\(property "Footprint" "([^"]*)"', b)
    veri = {"sembol": ad, "pin_kaynagi": kaynak, "footprint": fp.group(1) if fp else "", "pinler": pinler(b)}
    json.dump(veri, open(cikti, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(ad, "<-", kaynak, "|", len(veri["pinler"]), "pin adı |", veri["footprint"])


if __name__ == "__main__":
    main()
