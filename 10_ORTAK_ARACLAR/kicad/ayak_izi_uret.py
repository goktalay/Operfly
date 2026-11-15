"""Operfly ortak ayak izi kütüphanesini üretir (01_DONANIM/ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty).

Kullanım: python ayak_izi_uret.py <operfly_ayak.pretty klasörü>
Üretilen dosyalar eski biçim sürümüyle yazılır; ardından `kicad-cli fp upgrade <klasör>` ile güncel biçime çevrilir.
"""
import os
import sys

from mosaic_padleri import PADLER, konum


def mosaic():
    """Septentrio mosaic (LGA-239, 31 x 31 mm). Ölçüler üretici belgesinden (Hardware Manual 1.11.0, bölüm 3.2 ve 6.7.1):
    pad çapı 0,6 mm, adım 1,27 mm, 23 x 23 dizilimde dıştan üç sıra, A1 yok; lehim maskesi açıklığı pad + 75 um (NSMD).
    Kart çizimine geçmeden üreticinin güncel çizimiyle bir kez daha doğrulanır.
    """
    ad = "Septentrio_mosaic_LGA-239_31x31mm_P1.27mm"
    y = 15.5
    s = '(footprint "%s" (version 20240108) (generator "operfly") (generator_version "1") (layer "F.Cu")\n' % ad
    s += '\t(descr "Septentrio mosaic-X5 / mosaic-H GNSS modulu, LGA-239, 31x31 mm, adim 1.27 mm, pad 0.6 mm (uretici cizimiyle dogrulanacak)")\n'
    s += '\t(tags "GNSS Septentrio mosaic LGA")\n'
    s += '\t(property "Reference" "REF**" (at 0 %.2f 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n' % (-y - 1.6)
    s += '\t(property "Value" "%s" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n' % (ad, y + 1.6)
    s += '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += "\t(attr smd)\n"

    def cizgi(x1, y1, x2, y2, katman, w):
        return '\t(fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke (width %s) (type solid)) (layer "%s"))\n' % (x1, y1, x2, y2, w, katman)
    # Gövde (F.Fab): A1 köşesi pahlı
    p = 1.5
    for a, b in (((-y + p, -y), (y, -y)), ((y, -y), (y, y)), ((y, y), (-y, y)), ((-y, y), (-y, -y + p)), ((-y, -y + p), (-y + p, -y))):
        s += cizgi(a[0], a[1], b[0], b[1], "F.Fab", 0.1)
    # Serigrafi: köşe işaretleri, A1 köşesinde işaret yok + nokta
    k, u = y + 0.12, 2.0
    for sx, sy in ((1, -1), (1, 1), (-1, 1)):
        s += cizgi(sx * k, sy * k, sx * (k - u), sy * k, "F.SilkS", 0.12) + cizgi(sx * k, sy * k, sx * k, sy * (k - u), "F.SilkS", 0.12)
    s += '\t(fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS"))\n' % (-k - 0.5, -k - 0.5, -k - 0.37, -k - 0.5)
    c = y + 0.25
    s += '\t(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n' % (-c, -c, c, c)
    n = 0
    for isim, padler in PADLER.items():
        for no in padler:
            px, py = konum(no)
            s += '\t(pad "%s" smd circle (at %.2f %.2f) (size 0.6 0.6) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.075))\n' % (no, px, py)
            n += 1
    assert n == 239
    return ad, s + ")\n"


def main():
    klasor = sys.argv[1]
    os.makedirs(klasor, exist_ok=True)
    for ad, metin in (mosaic(),):
        yol = os.path.join(klasor, ad + ".kicad_mod")
        open(yol, "w", encoding="utf-8", newline="\n").write(metin)
        print("yazıldı:", yol)


if __name__ == "__main__":
    main()
