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
    def __init__(self, proje, baslik, kagit="A3", rev="A", tarih=""):
        self.proje, self.baslik, self.kagit, self.rev, self.tarih = proje, baslik, kagit, rev, tarih
        self.kok = uid(proje, "kok")
        self.lib = {}       # lib_id -> sembol bloğu (ad, kütüphane önekiyle)
        self.pinler = {}    # lib_id -> [(numara, ad, x, y, aci)]
        self.govde = []

    def kutuphane(self, lib_adi, yol, sembol):
        metin = open(yol, encoding="utf-8").read()
        m = re.search(r'\(symbol "%s"' % re.escape(sembol), metin)
        if not m:
            raise SystemExit("sembol yok: " + sembol)
        b = blok(metin, m.start())
        if re.search(r'\(extends "', b[:400]):
            raise SystemExit("türetilmiş sembol desteklenmiyor: " + sembol)
        lid = "%s:%s" % (lib_adi, sembol)
        self.lib[lid] = b.replace('(symbol "%s"' % sembol, '(symbol "%s"' % lid, 1)
        ps = []
        for pm in re.finditer(r"\(pin \w+ \w+", b):
            p = blok(b, pm.start())
            at = re.search(r"\(at ([-\d.]+) ([-\d.]+) (\d+)\)", p)
            ps.append((re.search(r'\(number "([^"]*)"', p).group(1), re.search(r'\(name "([^"]*)"', p).group(1),
                       float(at.group(1)), float(at.group(2)), int(at.group(3))))
        self.pinler[lid] = ps
        return lid

    def koy(self, lid, ref, deger, x, y, aglar, footprint=""):
        """aglar: {pin numarası veya pin adı: ağ adı}. Verilmeyen pinler bağlı değil sayılır."""
        x, y = round(x / 1.27) * 1.27, round(y / 1.27) * 1.27  # bağlantı ızgarasına oturt
        u = uid(self.proje, ref)
        s = '\t(symbol (lib_id "%s") (at %.2f %.2f 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "%s")\n' % (lid, x, y, u)
        ys = [p[3] for p in self.pinler[lid]]
        ust, alt = max(ys) + 5.08, min(ys) - 5.08
        for ad, dg, py, gizli in (("Reference", ref, ust, False), ("Value", deger, alt, False), ("Footprint", footprint, 0, True), ("Datasheet", "", 0, True)):
            s += '\t\t(property "%s" "%s" (at %.2f %.2f 0) (effects (font (size 1.27 1.27))%s))\n' % (ad, dg, x, y - py, " (hide yes)" if gizli else "")
        for no, ad, px, py, aci in self.pinler[lid]:
            s += '\t\t(pin "%s" (uuid "%s"))\n' % (no, uid(self.proje, ref, "pin", no))
        s += '\t\t(instances (project "%s" (path "/%s" (reference "%s") (unit 1))))\n\t)\n' % (self.proje, self.kok, ref)
        self.govde.append(s)
        kullanilan = set()
        for no, ad, px, py, aci in self.pinler[lid]:
            ag = aglar.get(no, aglar.get(ad))
            sx, sy = x + px, y - py
            if ag is None:
                self.govde.append('\t(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (sx, sy, uid(self.proje, ref, "nc", no)))
                continue
            kullanilan.add(no if no in aglar else ad)
            eaci, hiza = {0: (180, "right"), 180: (0, "left"), 90: (270, "right"), 270: (90, "left")}[aci]
            self.govde.append('\t(label "%s" (at %.2f %.2f %d) (effects (font (size 1.27 1.27)) (justify %s bottom)) (uuid "%s"))\n' % (ag, sx, sy, eaci, hiza, uid(self.proje, ref, "lbl", no)))
        eksik = set(aglar) - kullanilan
        if eksik:
            raise SystemExit("%s: sembolde olmayan pin(ler): %s" % (ref, sorted(eksik)))

    def metin(self, yazi, x, y, boyut=2.0):
        self.govde.append('\t(text "%s" (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f)) (justify left bottom)) (uuid "%s"))\n' % (yazi, x, y, boyut, boyut, uid(self.proje, "txt", yazi, x, y)))

    def yaz(self, yol):
        s = '(kicad_sch (version 20231120) (generator "eeschema") (generator_version "8.0") (uuid "%s") (paper "%s")\n' % (self.kok, self.kagit)
        s += '\t(title_block (title "%s") (date "%s") (rev "%s") (company "Operfly"))\n' % (self.baslik, self.tarih, self.rev)
        s += "\t(lib_symbols\n" + "".join("\t\t" + b + "\n" for b in self.lib.values()) + "\t)\n"
        s += "".join(self.govde)
        s += '\t(sheet_instances (path "/" (page "1")))\n)\n'
        open(yol, "w", encoding="utf-8", newline="\n").write(s)
        print("yazıldı:", yol)
