"""Kart (PCB) için otomatik yerleşim: şematikten kart dosyasını üretir, elemanları kart üzerine yerleştirir.

Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py <KART> <kök>`
Kart ayarları `01_DONANIM/<KART>/kicad/pcb_ayar.py` dosyasındaki AYAR sözlüğünden okunur (yoksa varsayılanlar):
    en, boy          kart ölçüsü (mm); verilmezse eleman alanından hesaplanır
    kenar            {"J1": ("K", None), ...} kenara oturacak konnektörler: K/G/D/B (kuzey/güney/doğu/batı) ve
                     kenar boyunca konum (mm; None = eşit dağıt)
    sabit            {"U7": (x, y, açı), ...} elle verilen konumlar
    delik            montaj deliği ayak izi (varsayılan M3) ya da None
    katman           bakır katman sayısı (varsayılan 4)
    kenar_otomatik   True ise ayarda geçmeyen J konnektörleri de kenara oturtulur (omurga portu batıya, anten
                     konnektörleri kuzeye, diğerleri en boş kenara); "ic" listesindeki konnektörler kart içinde kalır
    tohum            rastgele sayı tohumu (aynı tohum = aynı yerleşim)
Çıktı: `01_DONANIM/<KART>/kicad/<kök>.kicad_pcb` (yol çizilmemiş).

YÖNTEM: benzetimli tavlama. Maliyet = ağların çevre kutusu uzunluğu + küçük elemanları (kondansatör, direnç)
şematikte yanında durdukları entegrenin ilgili ucuna çeken yaylar + çakışma ve kart dışına taşma cezası.
Ardından çakışmalar kesin olarak giderilir. Bu bir mühendis yerleşimi DEĞİLDİR: ısıl tasarım, anahtarlamalı
güç döngüleri, RF ve yüksek hızlı hat kuralları gözetilmez; sonuç üretimden önce gözden geçirilir.
"""
import glob
import importlib.util
import math
import os
import random
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcb_uret  # noqa: E402

KOK = pcb_uret.KOK
MM = pcbnew.FromMM
DELIK_M3 = "MountingHole:MountingHole_3.2mm_M3"
# Ağ sınıfları (mm): açıklık, yol, geçiş çapı, geçiş deliği. Güç ağları adlarından tanınır.
# Açıklık 0,125 mm: 0,5 mm adımlı LGA kılıfların kendi uçları arası 0,129 mm olduğu için bundan büyük seçilemez.
SINIFLAR = {"Default": (0.125, 0.20, 0.60, 0.30)}
# İç katman düzlemleri: iç 1 toprak, iç 2 ana lojik beslemesi (kartta o ağ yoksa iç 2 yol çizimine kalır).
DUZLEMLER = {"In1.Cu": "GND", "In2.Cu": "+3V3"}
VARSAYILAN = {"en": None, "boy": None, "kenar": {}, "sabit": {}, "delik": DELIK_M3, "delik_ic": 3.5, "katman": 4,
              "tohum": 1, "bosluk": 0.30, "doluluk": 0.42, "oran": 1.35, "siniflar": {}, "guc_aglari": [], "duzlemler": DUZLEMLER,
              "kenar_otomatik": True, "ic": []}


def ayar_oku(kart):
    a = dict(VARSAYILAN)
    yol = os.path.join(KOK, "01_DONANIM", kart, "kicad", "pcb_ayar.py")
    if os.path.exists(yol):
        spec = importlib.util.spec_from_file_location("pcb_ayar", yol)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        a.update(m.AYAR)
    return a


def sema_konumlari(kart):
    """Her elemanın şematikteki yeri: {ref: (sayfa, x, y)}. Çok birimli sembolde ilk birim alınır."""
    konum = {}
    for yol in sorted(glob.glob(os.path.join(KOK, "01_DONANIM", kart, "kicad", "*.kicad_sch"))):
        t = open(yol, encoding="utf-8").read()
        for m in re.finditer(r'\n\t\(symbol\s*\(lib_id "[^"]+"\)\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)(.*?)(?=\n\t\(symbol\s*\(lib_id|\n\t\(sheet_instances|\Z)', t, re.S):
            r = re.search(r'\(reference "([^"]+)"\)', m.group(3))
            if r and r.group(1) not in konum and not r.group(1).startswith("#"):
                konum[r.group(1)] = (os.path.basename(yol), float(m.group(1)), float(m.group(2)))
    return konum


class Eleman:
    def __init__(self, fp):
        self.fp = fp
        self.ref = fp.GetReference()
        self.sabit = False
        self.x = self.y = 0.0
        self.rot = 0
        self.geo = {}   # açı -> (sol, üst, sağ, alt, [(uç no, ağ, dx, dy)])
        self.ped = {}   # açı -> uçların çevre kutusu
        self.ad = str(fp.GetFPID().GetLibItemName())
        fp.SetPosition(pcbnew.VECTOR2I(0, 0))
        for r in (0, 90, 180, 270):
            fp.SetOrientationDegrees(r)
            fp.BuildCourtyardCaches()
            kutu = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
            if kutu.GetWidth() <= 0:
                kutu = fp.GetBoundingBox(False)
            uclar = [(p.GetNumber(), p.GetNetname(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in fp.Pads()]
            self.geo[r] = (pcbnew.ToMM(kutu.GetLeft()), pcbnew.ToMM(kutu.GetTop()), pcbnew.ToMM(kutu.GetRight()), pcbnew.ToMM(kutu.GetBottom()), uclar)
            pk = [p.GetBoundingBox() for p in fp.Pads()]
            self.ped[r] = (min(pcbnew.ToMM(k.GetLeft()) for k in pk), min(pcbnew.ToMM(k.GetTop()) for k in pk),
                           max(pcbnew.ToMM(k.GetRight()) for k in pk), max(pcbnew.ToMM(k.GetBottom()) for k in pk)) if pk else self.geo[r][:4]
        fp.SetOrientationDegrees(0)
        g = self.geo[0]
        self.alan = (g[2] - g[0]) * (g[3] - g[1])
        self.uc_sayisi = len([u for u in g[4] if u[0]])

    def kutu(self, pay=0.0):
        g = self.geo[self.rot]
        return (self.x + g[0] - pay, self.y + g[1] - pay, self.x + g[2] + pay, self.y + g[3] + pay)

    def uclar(self):
        return self.geo[self.rot][4]

    def yaz(self):
        self.fp.SetOrientationDegrees(self.rot)
        self.fp.SetPosition(pcbnew.VECTOR2I(MM(self.x), MM(self.y)))


class Bolme:
    """Düzlemi karelere bölen arama yapısı: bir kutuya yakın elemanları hepsine bakmadan bulur."""

    def __init__(self, kare=4.0):
        self.kare, self.h, self.kayit = kare, {}, {}

    def _kareler(self, k):
        c = self.kare
        return [(ix, iy) for ix in range(int(k[0] // c), int(k[2] // c) + 1) for iy in range(int(k[1] // c), int(k[3] // c) + 1)]

    def ekle(self, anahtar, kutu):
        kareler = self._kareler(kutu)
        self.kayit[anahtar] = kareler
        for q in kareler:
            self.h.setdefault(q, set()).add(anahtar)

    def kaldir(self, anahtar):
        for q in self.kayit.pop(anahtar, ()):
            self.h[q].discard(anahtar)

    def yakin(self, kutu):
        s = set()
        for q in self._kareler(kutu):
            s |= self.h.get(q, set())
        return s


def acilis(e):
    """Yatay konnektörün ağzının baktığı yön (açı 0 iken): sinyal uçlarının ortasından gövde ortasına doğru."""
    g = e.geo[0]
    s = [(dx, dy) for no, _, dx, dy in g[4] if re.match(r"^[AB]?\d+$", no)]
    if not s:
        return None
    ox, oy = sum(p[0] for p in s) / len(s), sum(p[1] for p in s) / len(s)
    vx, vy = (g[0] + g[2]) / 2 - ox, (g[1] + g[3]) / 2 - oy
    if max(abs(vx), abs(vy)) < 0.6:
        return None   # dikey konnektör: belirgin yön yok
    return ("D" if vx > 0 else "B") if abs(vx) > abs(vy) else ("G" if vy > 0 else "K")


def kenara_oturt(e, kenar, konum, en, boy, ic=0.0):
    """Konnektörü ağzı dışarı bakacak biçimde kenara yaslar; dikey konnektör kenardan 1 mm içeride durur."""
    yon = acilis(e)
    sira = ["K", "D", "G", "B"]   # KiCad'de artı açı saat yönünün tersidir (y aşağı): K -> B -> G -> D
    if yon is None:
        e.rot, ic = (0 if kenar in "KG" else 90), 1.0
        g = e.geo[e.rot]
        if (kenar in "KG" and (g[2] - g[0]) < (g[3] - g[1])) or (kenar in "DB" and (g[3] - g[1]) < (g[2] - g[0])):
            e.rot = (e.rot + 90) % 360
    else:
        for r in (0, 90, 180, 270):
            if sira[(sira.index(yon) - r // 90) % 4] == kenar:
                e.rot = r
    g = e.geo[e.rot]
    if "EdgeMount" in e.ad:   # kart kenarını kıstıran konnektör: uçları kenardan bakır payı kadar içeride başlar
        g, ic = e.ped[e.rot], 0.35
    if kenar == "K":
        e.x, e.y = konum, ic - g[1]
    elif kenar == "G":
        e.x, e.y = konum, boy - ic - g[3]
    elif kenar == "B":
        e.x, e.y = ic - g[0], konum
    else:
        e.x, e.y = en - ic - g[2], konum
    e.sabit = True


def yerlestir(kart, kok, ayar=None):
    a = ayar_oku(kart)
    a.update(ayar or {})
    rnd = random.Random(a["tohum"])
    taslak, eksik = pcb_uret.uret(kart, kok, 200.0)
    if eksik:
        raise SystemExit("sembol-ayak izi uyumsuzluğu var; önce o düzeltilir")
    b = pcbnew.LoadBoard(taslak)
    for cizim in list(b.GetDrawings()):
        b.Remove(cizim)
    el = sorted((Eleman(fp) for fp in b.GetFootprints()), key=lambda e: e.ref)   # sıra sabit olsun: aynı tohum = aynı yerleşim
    idx = {e.ref: i for i, e in enumerate(el)}
    pay = a["bosluk"]
    # Kart ölçüsü
    alan = sum((e.geo[0][2] - e.geo[0][0] + 2 * pay) * (e.geo[0][3] - e.geo[0][1] + 2 * pay) for e in el)
    en, boy = a["en"], a["boy"]
    if en is None:
        toplam = alan / a["doluluk"]
        en = math.ceil(math.sqrt(toplam * a["oran"]) / 5.0) * 5.0
        boy = math.ceil(toplam / en / 5.0) * 5.0
    # Montaj delikleri
    delikler = []
    if a["delik"]:
        d = a["delik_ic"]
        for n, (hx, hy) in enumerate(((d, d), (en - d, d), (en - d, boy - d), (d, boy - d)), 1):
            fp = pcb_uret.ayak_izi(a["delik"])
            fp.SetReference("H%d" % n)
            fp.SetValue("M3")
            fp.SetBoardOnly(True)
            fp.Reference().SetVisible(False)
            b.Add(fp)
            h = Eleman(fp)
            h.x, h.y, h.sabit = hx, hy, True
            delikler.append(h)
    # Sabit ve kenar elemanları
    for ref, (x, y, r) in a["sabit"].items():
        e = el[idx[ref]]
        e.x, e.y, e.rot, e.sabit = x, y, r, True
    kenar_ayari = dict(a["kenar"])
    if a["kenar_otomatik"]:
        # Ayarda yeri verilmeyen konnektörler: omurga portu batıya, anten konnektörleri kuzeye, diğerleri en boş kenara.
        dolu = {"K": 0.0, "G": 0.0, "D": 0.0, "B": 0.0}
        uzunluk = {"K": en, "G": en, "D": boy, "B": boy}

        def genislik(e):
            g = e.geo[0]
            return max(g[2] - g[0], g[3] - g[1]) if acilis(e) is None else (g[2] - g[0] if acilis(e) in "KG" else g[3] - g[1])
        for ref, (kenar, _) in kenar_ayari.items():
            dolu[kenar] += genislik(el[idx[ref]]) + 2.0
        adaylar = [e for e in el if re.match(r"^J\d+$", e.ref) and e.ref not in kenar_ayari and e.ref not in a["sabit"] and e.ref not in a["ic"]]
        for e in sorted(adaylar, key=lambda e: (-genislik(e), e.ref)):
            if "Gecko" in e.ad:
                kenar = "B"
            elif "SMA" in e.ad:
                kenar = "K"
            else:
                kenar = min("DGKB", key=lambda k: (dolu[k] + genislik(e)) / (uzunluk[k] - 16.0))
            dolu[kenar] += genislik(e) + 2.0
            kenar_ayari[e.ref] = (kenar, None)
    gruplar = {}
    for ref, (kenar, konum) in kenar_ayari.items():
        gruplar.setdefault(kenar, []).append((ref, konum))
    for kenar, liste in gruplar.items():
        uzun = en if kenar in "KG" else boy
        bas, son = 8.0, uzun - 8.0
        liste.sort(key=lambda rk: int(re.sub(r"\D", "", rk[0]) or 0))
        serbest = [ref for ref, konum in liste if konum is None]
        for ref, konum in liste:
            if konum is not None:
                kenara_oturt(el[idx[ref]], kenar, konum, en, boy)
        # Yeri verilmeyenler: önce geçici oturt (açı belli olsun), sonra kenar boyunca eşit aralıkla diz.
        olcu = []
        for ref in serbest:
            e = el[idx[ref]]
            kenara_oturt(e, kenar, uzun / 2, en, boy)
            g = e.geo[e.rot]
            olcu.append((g[0], g[2]) if kenar in "KG" else (g[1], g[3]))
        toplam = sum(b_ - a_ for a_, b_ in olcu)
        if serbest:
            ara = (son - bas - toplam) / len(serbest)
            if ara < 1.0:
                raise SystemExit("kenar dolu (%s): konnektörler sığmıyor; kart büyütülür ya da kenar ayarı verilir" % kenar)
            konum = bas + ara / 2
            for ref, (a_, b_) in zip(serbest, olcu):
                kenara_oturt(el[idx[ref]], kenar, konum - a_, en, boy)
                konum += (b_ - a_) + ara
    hepsi = el + delikler
    hareketli = [i for i, e in enumerate(el) if not e.sabit]
    # Ağlar: (ağırlık, [(eleman, uç sırası)])
    aglar, eleman_aglari = [], [[] for _ in el]
    ag_uclari = {}
    for i, e in enumerate(el):
        for k, (no, ag, _, _) in enumerate(e.geo[0][4]):
            if ag:
                ag_uclari.setdefault(ag, []).append((i, k))
    guc = set()
    for ag, uclar in ag_uclari.items():
        if ag == "GND" or ag.endswith("GND") or ag.startswith("+") or len(uclar) > 14:
            guc.add(ag)
    duzlem_aglari = set(a["duzlemler"].values())
    for ag, uclar in sorted(ag_uclari.items()):
        if len(uclar) < 2 or ag in duzlem_aglari:
            continue
        w = 0.15 if ag in guc else 1.0
        n = len(aglar)
        aglar.append((w, uclar))
        for i in sorted({i for i, _ in uclar}):
            eleman_aglari[i].append(n)
    # Yaylar: küçük eleman -> şematikte en yakın entegrenin aynı ağdaki ucu
    sk = sema_konumlari(kart)
    buyuk = [i for i, e in enumerate(el) if e.uc_sayisi >= 4]
    yaylar, eleman_yaylari = [], [[] for _ in el]
    for i, e in enumerate(el):
        if e.uc_sayisi > 3 or e.ref not in sk:
            continue
        s, sx, sy = sk[e.ref]
        adaylar = []
        for j in buyuk:
            o = el[j]
            if o.ref not in sk or sk[o.ref][0] != s:
                continue
            ortak = sorted({u[1] for u in e.geo[0][4] if u[1]} & {u[1] for u in o.geo[0][4] if u[1]})
            sinyal = [g for g in ortak if g not in guc]
            besleme = [g for g in ortak if g in guc and g != "GND"]
            if sinyal or besleme:
                uzak = math.hypot(sk[o.ref][1] - sx, sk[o.ref][2] - sy)
                adaylar.append((0 if sinyal else 1, uzak, j, (sinyal or besleme)[0]))
        if not adaylar:
            continue
        _, _, j, ag = min(adaylar)
        ku = [k for k, u in enumerate(e.geo[0][4]) if u[1] == ag][0]
        hedef = [k for k, u in enumerate(el[j].geo[0][4]) if u[1] == ag]
        n = len(yaylar)
        yaylar.append((i, ku, j, hedef))
        eleman_yaylari[i].append(n)
        eleman_yaylari[j].append(n)

    def ag_maliyeti(n):
        w, uclar = aglar[n]
        xs, ys = [], []
        for i, k in uclar:
            e = el[i]
            u = e.geo[e.rot][4][k]
            xs.append(e.x + u[2])
            ys.append(e.y + u[3])
        return w * (max(xs) - min(xs) + max(ys) - min(ys))

    def yay_maliyeti(n):
        i, ku, j, hedef = yaylar[n]
        e, o = el[i], el[j]
        u = e.geo[e.rot][4][ku]
        px, py = e.x + u[2], e.y + u[3]
        og = o.geo[o.rot][4]
        return 1.5 * min(abs(o.x + og[k][2] - px) + abs(o.y + og[k][3] - py) for k in hedef)

    bolme = Bolme()
    for k, e in enumerate(hepsi):
        bolme.ekle(k, e.kutu(pay))

    def cakisma(i):
        e = el[i]
        l, t, r, bb = e.kutu(pay)
        c = max(0.0, -l) + max(0.0, -t) + max(0.0, r - en) + max(0.0, bb - boy)
        c *= 4.0
        for k in bolme.yakin((l, t, r, bb)):
            if k == i:
                continue
            ol, ot, orr, ob = hepsi[k].kutu(pay)
            dx, dy = min(r, orr) - max(l, ol), min(bb, ob) - max(t, ot)
            if dx > 0 and dy > 0:
                c += dx * dy + 0.5 * min(dx, dy)
        return c

    def yerel(i):
        return sum(ag_maliyeti(n) for n in eleman_aglari[i]) + sum(yay_maliyeti(n) for n in eleman_yaylari[i])

    # Başlangıç: şematik yerleşiminin küçültülmüşü (yoksa rastgele)
    xs = [sk[e.ref][1] for e in el if e.ref in sk] or [0, 1]
    ys = [sk[e.ref][2] for e in el if e.ref in sk] or [0, 1]
    for i in hareketli:
        e = el[i]
        if e.ref in sk:
            e.x = 4 + (en - 8) * (sk[e.ref][1] - min(xs)) / max(1.0, max(xs) - min(xs))
            e.y = 4 + (boy - 8) * (sk[e.ref][2] - min(ys)) / max(1.0, max(ys) - min(ys))
        else:
            e.x, e.y = rnd.uniform(4, en - 4), rnd.uniform(4, boy - 4)
        bolme.kaldir(i)
        bolme.ekle(i, e.kutu(pay))
    # Tavlama
    W = 6.0   # çakışma ağırlığı (sıcaklık düştükçe artar)
    adim = 120 * len(hareketli)
    T, T_son = 6.0, 0.02
    tur = 0
    while T > T_son:
        menzil = max(0.4, min(en, boy) * 0.5 * T / 6.0)
        for _ in range(adim):
            i = rnd.choice(hareketli)
            e = el[i]
            eski = (e.x, e.y, e.rot)
            sec = rnd.random()
            j = None
            if sec < 0.70:
                once = yerel(i) + W * cakisma(i)
                e.x = min(en - 1, max(1, e.x + rnd.gauss(0, menzil)))
                e.y = min(boy - 1, max(1, e.y + rnd.gauss(0, menzil)))
                sonra = yerel(i) + W * cakisma(i)
            elif sec < 0.85:
                once = yerel(i) + W * cakisma(i)
                e.rot = (e.rot + rnd.choice((90, 180, 270))) % 360
                sonra = yerel(i) + W * cakisma(i)
            else:
                j = rnd.choice(hareketli)
                if j == i:
                    continue
                o = el[j]
                eski_o = (o.x, o.y, o.rot)
                once = yerel(i) + yerel(j) + W * (cakisma(i) + cakisma(j))
                e.x, e.y, o.x, o.y = o.x, o.y, e.x, e.y
                bolme.kaldir(j)
                bolme.ekle(j, o.kutu(pay))
                bolme.kaldir(i)
                bolme.ekle(i, e.kutu(pay))
                sonra = yerel(i) + yerel(j) + W * (cakisma(i) + cakisma(j))
            d = sonra - once
            if d > 0 and rnd.random() >= math.exp(-d / T):
                e.x, e.y, e.rot = eski
                if j is not None:
                    o.x, o.y, o.rot = eski_o
                    bolme.kaldir(j)
                    bolme.ekle(j, o.kutu(pay))
                    bolme.kaldir(i)
                    bolme.ekle(i, e.kutu(pay))
            elif j is None:
                bolme.kaldir(i)
                bolme.ekle(i, e.kutu(pay))
        T *= 0.92
        W *= 1.06
        tur += 1
    # Kesin çakışma giderme: büyükten küçüğe, en yakın boş yere
    konan = Bolme()
    for k, e in enumerate(hepsi):
        if e.sabit:
            konan.ekle(k, e.kutu(pay))

    def bos_mu(e):
        l, t, r, bb = e.kutu(pay)
        if l < 0.3 or t < 0.3 or r > en - 0.3 or bb > boy - 0.3:
            return False
        for k in konan.yakin((l, t, r, bb)):
            ol, ot, orr, ob = hepsi[k].kutu(pay)
            if min(r, orr) - max(l, ol) > 1e-6 and min(bb, ob) - max(t, ot) > 1e-6:
                return False
        return True

    for i in sorted(hareketli, key=lambda i: -el[i].alan):
        e = el[i]
        e.x, e.y = round(e.x / 0.05) * 0.05, round(e.y / 0.05) * 0.05
        x0, y0 = e.x, e.y
        buldu = bos_mu(e)
        yaricap = 0.25
        while not buldu and yaricap < max(en, boy):
            n = max(8, int(2 * math.pi * yaricap / 0.25))
            for k in range(n):
                e.x = round((x0 + yaricap * math.cos(2 * math.pi * k / n)) / 0.05) * 0.05
                e.y = round((y0 + yaricap * math.sin(2 * math.pi * k / n)) / 0.05) * 0.05
                if bos_mu(e):
                    buldu = True
                    break
            yaricap += 0.25
        if not buldu:
            raise SystemExit("yer bulunamadı: %s (kart küçük; en/boy büyütülür)" % e.ref)
        konan.ekle(i, e.kutu(pay))
    # Son iyileştirme: çakışma yaratmayan ve maliyeti düşüren küçük kaymalar
    for _ in range(25):
        for i in hareketli:
            e = el[i]
            konan.kaldir(i)
            en_iyi = (yerel(i), e.x, e.y, e.rot)
            x0, y0, r0 = e.x, e.y, e.rot
            for dx, dy, dr in [(s * a_, 0, 0) for s in (-1, 1) for a_ in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)] + [(0, s * a_, 0) for s in (-1, 1) for a_ in (0.1, 0.25, 0.5, 1.0, 2.0, 4.0)] + [(0, 0, 90), (0, 0, 180), (0, 0, 270)]:
                e.x, e.y, e.rot = x0 + dx, y0 + dy, (r0 + dr) % 360
                if bos_mu(e):
                    m = yerel(i)
                    if m < en_iyi[0] - 1e-6:
                        en_iyi = (m, e.x, e.y, e.rot)
            _, e.x, e.y, e.rot = en_iyi
            konan.ekle(i, e.kutu(pay))
    for e in hepsi:
        e.yaz()
    # Kart sınırı, katmanlar, kurallar
    kose = [(0, 0), (en, 0), (en, boy), (0, boy)]
    for (ax, ay), (bx, by) in zip(kose, kose[1:] + kose[:1]):
        s = pcbnew.PCB_SHAPE(b)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(ax), MM(ay)))
        s.SetEnd(pcbnew.VECTOR2I(MM(bx), MM(by)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        b.Add(s)
    b.SetCopperLayerCount(a["katman"])
    for fp in b.GetFootprints():   # yazılar: referans gövdenin ortasında, üretim katmanında (serigrafide kalabalık olmasın)
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetPosition(fp.GetPosition())
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(MM(0.5), MM(0.5)))
        fp.Reference().SetTextThickness(MM(0.08))
        fp.Value().SetVisible(False)
    cikti = os.path.join(KOK, "01_DONANIM", kart, "kicad", kok + ".kicad_pcb")
    pcbnew.SaveBoard(cikti, b)
    tel = sum(ag_maliyeti(n) / aglar[n][0] for n in range(len(aglar)) if aglar[n][0] == 1.0)
    print("yerleşim: %s | kart %.0f x %.0f mm, %d eleman, sinyal ağlarının kutu uzunluğu %.0f mm, doluluk %%%.0f"
          % (os.path.relpath(cikti, KOK), en, boy, len(el), tel, 100 * alan / (en * boy)))
    return cikti


if __name__ == "__main__":
    yerlestir(sys.argv[1], sys.argv[2])
