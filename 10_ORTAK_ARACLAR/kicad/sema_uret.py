"""Basit şematik üreteci: semboller yerleştirilir, her pinin ucuna ağ etiketi konur.

Tel çizilmez; aynı adı taşıyan etiketler aynı ağdır. Atanmamış pinlere "bağlı değil" işareti konur.
Üretilen dosya eski biçim sürümüyle yazılır; ardından `kicad-cli sch upgrade` ile güncel biçime çevrilir.
"""
import re
import uuid

from pin_cikar import blok

NS = uuid.UUID("6f1d2c7e-0a57-4c57-9f0e-0f0e0f1a2b3c")


def uid(*p):
    return str(uuid.uuid5(NS, "/".join(str(x) for x in p)))


class Sema:
    def __init__(self, proje, baslik, kagit="A3", rev="A", tarih="", ust=None, ad="kok", genel_etiket=False):
        """ust: bu sayfayı içeren kök Sema (alt sayfalar için). genel_etiket: sayfalar arası (global) etiket kullan."""
        self.proje, self.baslik, self.kagit, self.rev, self.tarih = proje, baslik, kagit, rev, tarih
        self.kok = uid(proje, "dosya", ad)
        self.ust, self.ad, self.genel = ust, ad, genel_etiket
        self.yol = "/" + self.kok   # sembol örnek yolu; alt sayfada kök tarafından ayarlanır
        self.lib = {}       # lib_id -> sembol bloğu (ad, kütüphane önekiyle)
        self.pinler = {}    # lib_id -> [(numara, ad, x, y, aci)]
        self.govde = []
        self.sayfa_no = 1

    def alt_sayfa(self, alt, dosya, x, y, w=50.8, h=20.32):
        """Kök sayfaya bir alt sayfa kutusu koyar ve alt sayfanın örnek yolunu ayarlar."""
        self.sayfa_no += 1
        su = uid(self.proje, "sayfa", alt.ad)
        alt.yol = "/%s/%s" % (self.kok, su)
        s = '\t(sheet (at %.2f %.2f) (size %.2f %.2f) (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000)) (uuid "%s")\n' % (x, y, w, h, su)
        s += '\t\t(property "Sheetname" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left bottom)))\n' % (alt.ad, x, y - 0.7)
        s += '\t\t(property "Sheetfile" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left top)))\n' % (dosya, x, y + h + 0.6)
        s += '\t\t(instances (project "%s" (path "/%s" (page "%d"))))\n\t)\n' % (self.proje, self.kok, self.sayfa_no)
        self.govde.append(s)

    def kutuphane(self, lib_adi, yol, sembol):
        metin = open(yol, encoding="utf-8").read()
        m = re.search(r'\(symbol "%s"' % re.escape(sembol), metin)
        if not m:
            raise SystemExit("sembol yok: " + sembol)
        b = blok(metin, m.start())
        e = re.search(r'\(extends "([^"]+)"\)', b[:400])
        if e:  # türetilmiş sembol: temel sembolün çizimi ve pinleri bu adla kopyalanır
            temel = e.group(1)
            tm = re.search(r'\(symbol "%s"' % re.escape(temel), metin)
            tureyen = b
            b = blok(metin, tm.start())
            b = b.replace('(symbol "%s"' % temel, '(symbol "%s"' % sembol, 1)
            # türetilmiş sembolün kendi özellikleri (değer, ayak izi, veri sayfası...) temelinkilerin yerini alır
            for pm in re.finditer(r'\(property "([^"]+)"', tureyen):
                yeni = blok(tureyen, pm.start())
                em = re.search(r'\(property "%s"' % re.escape(pm.group(1)), b)
                if em:
                    eski = blok(b, em.start())
                    b = b.replace(eski, yeni, 1)
                else:
                    i = b.index("(symbol ", 1)
                    b = b[:i] + yeni + "\n\t\t" + b[i:]
            b = re.sub(r'\(symbol "%s_(\d+_\d+)"' % re.escape(temel), '(symbol "%s_\\1"' % sembol, b)
        lid = "%s:%s" % (lib_adi, sembol)
        self.lib[lid] = b.replace('(symbol "%s"' % sembol, '(symbol "%s"' % lid, 1)
        ps = []
        for pm in re.finditer(r"\(pin \w+ \w+", b):
            p = blok(b, pm.start())
            at = re.search(r"\(at ([-\d.]+) ([-\d.]+) (\d+)\)", p)
            ps.append((re.search(r'\(number "([^"]*)"', p).group(1), re.search(r'\(name "([^"]*)"', p).group(1),
                       float(at.group(1)), float(at.group(2)), int(at.group(3))))
        self.pinler[lid] = ps
        # Çok birimli semboller (ör. USB ve Ethernet uçları ayrı birimde): her pinin birimi. 0 = tüm birimlerde ortak.
        birim = {}
        for sm in re.finditer(r'\(symbol "[^"]*_(\d+)_\d+"', b):
            alt = blok(b, sm.start())
            for no in re.findall(r'\(number "([^"]*)"', alt):
                birim[no] = max(1, int(sm.group(1)))
        if not hasattr(self, "birim"):
            self.birim = {}
        self.birim[lid] = birim
        return lid

    def koy(self, lid, ref, deger, x, y, aglar, footprint="", dnp=False):
        """aglar: {pin numarası veya pin adı: ağ adı}. Verilmeyen pinler bağlı değil sayılır."""
        if footprint:
            if not hasattr(self, "ayak_izleri"):
                self.ayak_izleri = set()
            self.ayak_izleri.add(footprint)
        x, y = round(x / 1.27) * 1.27, round(y / 1.27) * 1.27  # bağlantı ızgarasına oturt
        birim = getattr(self, "birim", {}).get(lid, {})
        birimler = sorted(set(birim.values())) or [1]
        kullanilan = set()
        for bn in birimler:   # çok birimli sembolde birimler yan yana konur
            pinler = [p for p in self.pinler[lid] if birim.get(p[0], 1) == bn]
            bx = round((x + (bn - birimler[0]) * getattr(self, "birim_araligi", 76.2)) / 1.27) * 1.27
            u = uid(self.proje, ref) if bn == birimler[0] else uid(self.proje, ref, "birim", bn)
            s = '\t(symbol (lib_id "%s") (at %.2f %.2f 0) (unit %d) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp %s) (uuid "%s")\n' % (lid, bx, y, bn, "yes" if dnp else "no", u)
            ys = [p[3] for p in pinler]
            ust, alt = max(ys) + 5.08, min(ys) - 5.08
            dikey = len(pinler) <= 2 and all(p[2] == 0 for p in pinler)  # uçları üstte ve altta olan eleman
            for ad, dg, py, gizli in (("Reference", ref, ust, False), ("Value", deger, alt, False), ("Footprint", footprint, 0, True), ("Datasheet", "", 0, True)):
                px, hiza = bx, ""
                if dikey and not gizli:  # yazılar yana: üstte ve altta ağ etiketleri duruyor
                    px, py, hiza = bx + 2.54, (1.27 if ad == "Reference" else -1.27), " (justify left)"
                s += '\t\t(property "%s" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27))%s%s))\n' % (ad, dg, px, y - py, hiza, " (hide yes)" if gizli else "")
            for no, ad, px, py, aci in pinler:
                s += '\t\t(pin "%s" (uuid "%s"))\n' % (no, uid(self.proje, ref, "pin", no))
            s += '\t\t(instances (project "%s" (path "%s" (reference "%s") (unit %d))))\n\t)\n' % (self.proje, self.yol, ref, bn)
            self.govde.append(s)
            konulan = set()   # ayni noktada ust uste duran uclar (cok sayida GND gibi) tek etiket alir
            for no, ad, px, py, aci in pinler:
                ag = aglar.get(no, aglar.get(ad))
                sx, sy = bx + px, y - py
                if ag is not None:
                    kullanilan.add(no if no in aglar else ad)
                if (round(sx, 2), round(sy, 2), ag) in konulan:
                    continue
                konulan.add((round(sx, 2), round(sy, 2), ag))
                if ag is None:
                    self.govde.append('\t(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (sx, sy, uid(self.proje, ref, "nc", no)))
                    continue
                eaci, hiza = {0: (180, "right"), 180: (0, "left"), 90: (270, "right"), 270: (90, "left")}[aci]
                if self.genel:
                    self.govde.append('\t(global_label "%s" (shape passive) (at %.2f %.2f %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (ag, sx, sy, eaci, hiza, uid(self.proje, ref, "lbl", no)))
                else:
                    self.govde.append('\t(label "%s" (at %.2f %.2f %d) (effects (font (size 1.27 1.27)) (justify %s bottom)) (uuid "%s"))\n' % (ag, sx, sy, eaci, hiza, uid(self.proje, ref, "lbl", no)))
        eksik = set(aglar) - kullanilan
        if eksik:
            raise SystemExit("%s: sembolde olmayan pin(ler): %s" % (ref, sorted(eksik)))

    def bayrak(self, ag, x, y, sembol_dizini):
        """Bir ağı "beslenen ağ" olarak işaretler (PWR_FLAG). Besleme pasif eleman üzerinden geldiğinde gerekir."""
        import os
        lid = "power:PWR_FLAG"
        if lid not in self.lib:
            self.kutuphane("power", os.path.join(sembol_dizini, "power.kicad_sym"), "PWR_FLAG")
        self._bayrak_no = getattr(self, "_bayrak_no", 0) + 1
        self.koy(lid, "#FLG_%s_%02d" % (self.ad, self._bayrak_no), "PWR_FLAG", x, y, {"1": ag})

    def metin(self, yazi, x, y, boyut=2.0):
        self.govde.append('\t(text "%s" (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f)) (justify left bottom)) (uuid "%s"))\n' % (yazi, x, y, boyut, boyut, uid(self.proje, "txt", yazi, x, y)))

    def yaz(self, yol):
        s = '(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0") (uuid "%s") (paper "%s")\n' % (self.kok, self.kagit)
        s += '\t(title_block (title "%s") (date "%s") (rev "%s") (company "Operfly"))\n' % (self.baslik, self.tarih, self.rev)
        s += "\t(lib_symbols\n" + "".join("\t\t" + b + "\n" for b in self.lib.values()) + "\t)\n"
        s += "".join(self.govde)
        s += ('\t(sheet_instances (path "/" (page "1")))\n' if self.ust is None else "") + ")\n"
        open(yol, "w", encoding="utf-8", newline="\n").write(s)
        print("yazıldı:", yol)


def kutuphane_tablolari(dizin, semalar, ozel=None):
    """Proje kütüphane tablolarını (sym-lib-table, fp-lib-table) şematikte kullanılanlardan üretir.

    ozel: {kütüphane adı: uri} - KiCad standart kütüphanesi olmayanlar (ör. ortak Operfly kütüphanesi).
    """
    import os
    ozel = ozel or {}
    sym, fp = set(), set()
    for s in semalar:
        sym.update(l.split(":")[0] for l in s.lib)
        fp.update(f.split(":")[0] for f in getattr(s, "ayak_izleri", ()) if ":" in f)
    def tablo(ad, adlar, degisken, uzanti):
        t = "(%s\n  (version 7)\n" % ad
        for n in sorted(adlar):
            uri = ozel.get(n, "${%s}/%s%s" % (degisken, n, uzanti))
            t += '  (lib (name "%s")(type "KiCad")(uri "%s")(options "")(descr ""))\n' % (n, uri)
        return t + ")\n"
    open(os.path.join(dizin, "sym-lib-table"), "w", encoding="utf-8", newline="\n").write(tablo("sym_lib_table", sym, "KICAD10_SYMBOL_DIR", ".kicad_sym"))
    open(os.path.join(dizin, "fp-lib-table"), "w", encoding="utf-8", newline="\n").write(tablo("fp_lib_table", fp, "KICAD10_FOOTPRINT_DIR", ".pretty"))


def kicad_sembol_dizini():
    """KiCad'in sembol kütüphanesi klasörünü bulur (OPERFLY_KICAD_SYMBOLS ile değiştirilebilir)."""
    import glob
    import os
    adaylar = [os.environ.get("OPERFLY_KICAD_SYMBOLS", "")]
    adaylar += sorted(glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "KiCad", "*", "share", "kicad", "symbols")), reverse=True)
    adaylar += sorted(glob.glob(r"C:\Program Files\KiCad\*\share\kicad\symbols"), reverse=True)
    adaylar += ["/usr/share/kicad/symbols", "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"]
    for a in adaylar:
        if a and os.path.isdir(a):
            return a
    raise SystemExit("KiCad sembol klasörü bulunamadı; OPERFLY_KICAD_SYMBOLS ortam değişkenini ayarlayın")
