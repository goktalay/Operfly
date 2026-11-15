"""Operfly ortak ayak izi kütüphanesini üretir (01_DONANIM/ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty).

Kullanım: python ayak_izi_uret.py <operfly_ayak.pretty klasörü> [ayak izi adı]
Üretilen dosyalar eski biçim sürümüyle yazılır; ardından `kicad-cli fp upgrade <klasör>` ile güncel biçime çevrilir.
Biçim çevirisi her seferinde yeni kimlikler (uuid) yazdığı için yalnızca değişen ayak izi adıyla üretilir;
ad verilmezse hepsi yeniden yazılır.
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


def rfd900ux_smt():
    """RFDesign RFD900ux-SMT / RFD868ux-SMT (21 x 29 mm, kenar pedli). Olculer uretici veri sayfasindan (V1.3, Tablo 5-1,
    Sekil 5-1, 5-2, 6-2): kenar pedi 2,4 x 1,0 mm; sutunlar arasi 21,2 mm; adim 2,0 mm (1-11 ve 18-28), anten grubunda
    1,5 mm (12-14, 15-17), iki grup arasi 3,5 mm; isi pedleri 8 x 6,6 mm, merkezleri arasi 11,5 mm, ilki 1. pedden 7,0 mm;
    gecis delikleri 1,5 mm adimla 5 x 5; lehim pastasi 7 x 6 mm alanda 0,5 mm aralikli dort pencere.
    Sekildeki olculerden cikarildi; kart cizimine gecmeden ureticinin Altium bileseniyle karsilastirilacak.
    Yon: 1. ped sol ustte; sol sutun yukaridan asagi 1-14, sag sutun asagidan yukari 15-28 (uretici sekli 180 derece donuk).
    """
    ad = "RFDesign_RFD900ux-SMT"
    gx, gy = 10.5, 14.5
    s = '(footprint "%s" (version 20240108) (generator "operfly") (generator_version "1") (layer "F.Cu")\n' % ad
    s += '\t(descr "RFDesign RFD900ux-SMT / RFD868ux-SMT radyo modulu, 21x29 mm, 28 kenar pedi + 2 isi pedi (uretici bileseniyle dogrulanacak)")\n'
    s += '\t(tags "RFD900ux RFD868ux SMT radio modem")\n'
    s += '\t(property "Reference" "REF**" (at 0 %.2f 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n' % (-gy - 1.6)
    s += '\t(property "Value" "%s" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n' % (ad, gy + 1.6)
    s += '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += "\t(attr smd)\n"
    s += '\t(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))\n' % (-gx, -gy, gx, gy)
    s += '\t(fp_line (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))\n' % (-gx, -gy - 0.12, gx, -gy - 0.12)
    s += '\t(fp_line (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))\n' % (-gx, gy + 0.12, gx, gy + 0.12)
    s += '\t(fp_circle (center %.2f %.2f) (end %.2f %.2f) (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS"))\n' % (-12.6, -13.0, -12.47, -13.0)
    s += '\t(fp_rect (start -12.05 %.2f) (end 12.05 %.2f) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n' % (-gy - 0.25, gy + 0.25)
    ys = [-13.0 + 2.0 * i for i in range(11)] + [10.5, 12.0, 13.5]          # pedler 1..14, yukaridan asagi
    konum = {i + 1: (-10.6, y) for i, y in enumerate(ys)}
    konum.update({28 - i: (10.6, y) for i, y in enumerate(ys)})              # 28 ustte, 15 altta
    assert len(konum) == 28 and konum[15] == (10.6, 13.5) and konum[18] == (10.6, 7.0)
    for no in range(1, 29):
        s += '\t(pad "%d" smd rect (at %.2f %.2f) (size 2.4 1) (layers "F.Cu" "F.Paste" "F.Mask"))\n' % (no, konum[no][0], konum[no][1])
    for no, cy in ((29, -6.0), (30, 5.5)):
        s += '\t(pad "%d" smd rect (at 0 %.2f) (size 8 6.6) (layers "F.Cu" "F.Mask"))\n' % (no, cy)
        for dx in (-1.875, 1.875):
            for dy in (-1.625, 1.625):
                s += '\t(pad "" smd rect (at %.3f %.3f) (size 3.25 2.75) (layers "F.Paste"))\n' % (dx, cy + dy)
        for i in range(5):
            for j in range(5):
                s += '\t(pad "%d" thru_hole circle (at %.2f %.2f) (size 0.6 0.6) (drill 0.3) (layers "*.Cu"))\n' % (no, (i - 2) * 1.5, cy + (j - 2) * 1.5)
    return ad, s + ")\n"


def main():
    klasor = sys.argv[1]
    os.makedirs(klasor, exist_ok=True)
    for ad, metin in (mosaic(), rfd900ux_smt()):
        if len(sys.argv) > 2 and ad != sys.argv[2]:
            continue
        yol = os.path.join(klasor, ad + ".kicad_mod")
        open(yol, "w", encoding="utf-8", newline="\n").write(metin)
        print("yazıldı:", yol)


if __name__ == "__main__":
    main()
