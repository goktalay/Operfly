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


def pmddl():
    """Microhard pMDDL OEM (pMDDL2350/2450/2550; 26,5 x 33 mm, 80 kenar pedi + alt toprak duzlemi). Olculer uretici
    isletme kilavuzundan (v1.4.2, Cizim 3-1, 3-2, 3-3): ped 1,83 x 0,81 mm, adim 1,27 mm; yan sutunlar distan disa 27,99 mm
    (24'er ped), ust ve alt siralar distan disa 34,34 mm (16'sar ped); toprak duzlemi 22,35 x 28,70 mm;
    lehim pastasi toprak duzleminde 1,03 x 2,55 mm pencereler, sasirtmali 5-4 dizilim, sutun adimi 4,12 mm, satir araligi 1,00 mm.
    Yon (ustten bakis, Cizim 3-5): 1-24 sol sutun yukaridan asagi, 25-40 alt sira soldan saga, 41-64 sag sutun asagidan yukari,
    65-80 ust sira sagdan sola; antenler ust kenarda. Toprak duzlemi kilavuzda numarasiz, burada 81.
    Kart cizimine gecmeden ureticinin guncel cizimiyle karsilastirilacak.
    """
    ad = "Microhard_pMDDL_OEM"
    gx, gy = 13.25, 16.5
    s = '(footprint "%s" (version 20240108) (generator "operfly") (generator_version "1") (layer "F.Cu")\n' % ad
    s += '\t(descr "Microhard pMDDL OEM radyo modulu, 26.5x33 mm, 80 kenar pedi + toprak duzlemi (uretici cizimiyle dogrulanacak)")\n'
    s += '\t(tags "Microhard pMDDL2450 OEM radio module")\n'
    s += '\t(property "Reference" "REF**" (at 0 %.2f 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n' % (-19.2)
    s += '\t(property "Value" "%s" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n' % (ad, 19.2)
    s += '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += "\t(attr smd)\n"
    s += '\t(fp_rect (start %.2f %.2f) (end %.2f %.2f) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))\n' % (-gx, -gy, gx, gy)
    s += '\t(fp_circle (center %.2f %.2f) (end %.2f %.2f) (stroke (width 0.25) (type solid)) (fill none) (layer "F.SilkS"))\n' % (-15.0, -14.605, -14.87, -14.605)
    s += '\t(fp_rect (start -14.25 -17.42) (end 14.25 17.42) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n'
    xs, ys = 27.99 / 2 - 1.83 / 2, 34.34 / 2 - 1.83 / 2      # sutun ve sira merkezleri
    konum = {}
    for i in range(24):
        konum[1 + i] = (-xs, (i - 11.5) * 1.27, 1.83, 0.81)       # sol: yukaridan asagi
        konum[41 + i] = (xs, (11.5 - i) * 1.27, 1.83, 0.81)       # sag: asagidan yukari
    for i in range(16):
        konum[25 + i] = ((i - 7.5) * 1.27, ys, 0.81, 1.83)        # alt: soldan saga
        konum[65 + i] = ((7.5 - i) * 1.27, -ys, 0.81, 1.83)       # ust: sagdan sola
    assert len(konum) == 80
    for no in range(1, 81):
        x, y, w, h = konum[no]
        s += '\t(pad "%d" smd rect (at %.3f %.3f) (size %.2f %.2f) (layers "F.Cu" "F.Paste" "F.Mask"))\n' % (no, x, y, w, h)
    s += '\t(pad "81" smd rect (at 0 0) (size 22.35 28.7) (layers "F.Cu" "F.Mask"))\n'
    for r in range(7):
        n = 5 if r % 2 == 0 else 4
        for c in range(n):
            s += '\t(pad "" smd rect (at %.2f %.2f) (size 1.03 2.55) (layers "F.Paste"))\n' % ((c - (n - 1) / 2) * 4.12, (r - 3) * 3.55)
    return ad, s + ")\n"


def ksz9567r():
    """Microchip KSZ9567R: 128 uçlu TQFP, 14 x 14 mm, adım 0,4 mm, 10 x 10 mm alt pedli.
    Ölçüler üreticinin önerilen lehim deseninden (Microchip çizimi C04-2418B, veri sayfası DS00002329 Şekil 8-3):
    ped 0,20 x 1,54 mm, karşılıklı ped merkezleri arası 15,40 mm, orta ped 10,50 x 10,50 mm.
    Isı geçişleri (üretici önerisi: çap 0,33 mm, adım 1,20 mm) kart çiziminde orta pedin içine yerleştirilir.
    Orta pedin lehim pastası 4 x 4 pencereye bölünmüştür (pedin yaklaşık yüzde 58'i).
    """
    ad = "Microchip_TQFP-128-1EP_14x14mm_P0.4mm_EP10x10mm"
    s = '(footprint "%s" (version 20240108) (generator "operfly") (generator_version "1") (layer "F.Cu")\n' % ad
    s += '\t(descr "Microchip 128 uclu TQFP, 14x14 mm, adim 0.4 mm, 10x10 mm alt pedli (cizim C04-2418B); isi gecisleri kart ciziminde eklenir")\n'
    s += '\t(tags "TQFP QFP Microchip KSZ9567R")\n'
    s += '\t(property "Reference" "REF**" (at 0 -9.9 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
    s += '\t(property "Value" "%s" (at 0 9.9 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))\n' % ad
    s += '\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Datasheet" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += '\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))\n'
    s += "\t(attr smd)\n"

    def cizgi(x1, y1, x2, y2, katman, w):
        return '\t(fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke (width %s) (type solid)) (layer "%s"))\n' % (x1, y1, x2, y2, w, katman)
    g, p = 7.0, 1.0   # gövde yarı kenarı, 1. uç köşesindeki pah
    for a, b in (((-g + p, -g), (g, -g)), ((g, -g), (g, g)), ((g, g), (-g, g)), ((-g, g), (-g, -g + p)), ((-g, -g + p), (-g + p, -g))):
        s += cizgi(a[0], a[1], b[0], b[1], "F.Fab", 0.1)
    k, u = g + 0.11, 0.5   # serigrafi: köşe işaretleri; 1. uç köşesinde nokta
    for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1)):
        s += cizgi(sx * k, sy * k, sx * (k - u), sy * k, "F.SilkS", 0.12) + cizgi(sx * k, sy * k, sx * k, sy * (k - u), "F.SilkS", 0.12)
    s += '\t(fp_circle (center -8.9 -6.9) (end -8.75 -6.9) (stroke (width 0.3) (type solid)) (fill none) (layer "F.SilkS"))\n'
    s += '\t(fp_rect (start -8.72 -8.72) (end 8.72 8.72) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))\n'
    m, n = 7.70, 0   # ped merkezi (15,40 / 2)
    for i in range(32):
        d = -6.2 + 0.4 * i
        for no, x, y, w, h in ((1 + i, -m, d, 1.54, 0.20), (33 + i, d, m, 0.20, 1.54), (65 + i, m, -d, 1.54, 0.20), (97 + i, -d, -m, 0.20, 1.54)):
            s += '\t(pad "%d" smd rect (at %.2f %.2f) (size %.2f %.2f) (layers "F.Cu" "F.Paste" "F.Mask"))\n' % (no, x, y, w, h)
            n += 1
    assert n == 128
    s += '\t(pad "129" smd rect (at 0 0) (size 10.50 10.50) (layers "F.Cu" "F.Mask"))\n'
    for i in range(4):
        for j in range(4):
            s += '\t(pad "" smd rect (at %.2f %.2f) (size 2.00 2.00) (layers "F.Paste"))\n' % (-3.75 + 2.5 * i, -3.75 + 2.5 * j)
    return ad, s + ")\n"


def main():
    klasor = sys.argv[1]
    os.makedirs(klasor, exist_ok=True)
    for ad, metin in (mosaic(), rfd900ux_smt(), pmddl(), ksz9567r()):
        if len(sys.argv) > 2 and ad != sys.argv[2]:
            continue
        yol = os.path.join(klasor, ad + ".kicad_mod")
        open(yol, "w", encoding="utf-8", newline="\n").write(metin)
        print("yazıldı:", yol)


if __name__ == "__main__":
    main()
