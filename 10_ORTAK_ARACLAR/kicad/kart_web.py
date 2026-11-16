"""Çizilmiş kartları (PCB) donanım şeması sayfasında (06_PANELLER/donanim-semasi) döndürülebilir 3B model olarak
gösterilecek biçime çevirir.

Çalıştırma (depo kökünden): python 10_ORTAK_ARACLAR/kicad/kart_web.py [KART ...]
Çıktı: out/kart_web/kart/liste.js (hangi donanımın kartı var; ölçü, katman, denetim durumu) ve
out/kart_web/kart/<donanım>.js (kartın 3B modeli, betik dosyası içinde). Çıktı depoya eklenmez; sayfa yayımlanırken
index.html ile birlikte yüklenir. Kart dosyası (01_DONANIM/<KART>/kicad/<kök>.kicad_pcb) olmayan donanım atlanır;
dosya sonradan gelince `python 10_ORTAK_ARACLAR/kicad/kart_web.py <KART>` ile yalnız o kart üretilir.

Gerekenler: kicad-cli (KiCad 10) ve numpy. Eleman gövdeleri için KiCad'in 3B model kitaplığı kurulu olmalı
(Debian/Ubuntu: kicad-packages3d; yeri KICAD10_3DMODEL_DIR, yoksa /usr/share/kicad/3dmodels denenir). Kitaplık yoksa
ya da bir elemanın modeli yoksa o eleman gövdesiz (yalnız pedleriyle) çıkar; kaç elemanın gövdesi olduğu listeye yazılır.

Nasıl çalışır: kicad-cli kartı GLB olarak verir (bakır yollar, pedler, geçişler, lehim maskesi, serigrafi, eleman
gövdeleri). O dosya telefonda açılamayacak kadar büyük ve parçalıdır (her yüz ayrı çizim); burada küçültülür:
  - aynı renkli parçalar tek çizim grubunda birleştirilir, çakışan noktalar kaynaştırılır;
  - bakırın yalnız dışarıdan görünen yüzü tutulur (35 mikronluk yan duvarlar ve kart içinde kalan yüzler atılır);
  - koordinatlar 16 bite indirilir, fark kodlaması yapılır, sonuç zlib ile sıkıştırılıp base64 olarak yazılır
    (altı harf işaretle değiştirilir; nedeni HARF_DEGISIMI satırında).
Katmanlar arası yükseklik farkları (bakır, maske, serigrafi; 5-35 mikron) ekranda titreşmesin diye 3 katına açılır.
Yüzey normalleri saklanmaz; sayfadaki görüntüleyici düz gölgelendirme yapar. Biçimi sayfadaki `kartCoz` işlevi okur.
"""
import base64
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from sema_web import KARTLAR, KOK  # noqa: E402  (aynı donanım kimlikleri ve adları)

CIKTI = os.path.join(KOK, "out", "kart_web", "kart")
# base64 metninde rastlantıyla yasak bir ad (13_DOKUMANTASYON/marka_yasak_listesi.txt) oluşmasın diye bu harfler
# yazılmaz; yerlerine base64 abecesinde olmayan işaretler konur (sayfa geri çevirir). marka_denetle.py out/ altını da tarar.
HARF_DEGISIMI = ("xXaAqQ", "-_.~!*")
KATMAN_ACMA = 3.0      # kart yüzeyine yapışık katmanların yükseklik farkı kaç katına açılır
KATMAN_BANDI = 0.1     # mm; kart yüzeyinden bu kadar yüksekliğe kadar olan bölge açılır
# Kart parçaları ağ adının sonundan tanınır; sıra çizim sırasıdır (saydamlar en sonda).
KART_PARCALARI = ["PCB", "copper", "via", "pad", "silkscreen", "soldermask"]
TUR = {"PCB": "govde", "copper": "bakir", "via": "bakir", "pad": "ped", "silkscreen": "yazi", "soldermask": "maske"}


def glb_oku(yol):
    d = open(yol, "rb").read()
    if d[:4] != b"glTF":
        raise SystemExit("GLB değil: %s" % yol)
    n = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + n])
    return j, memoryview(d)[20 + n + 8:]


def erisim(j, veri, i):
    a = j["accessors"][i]
    bv = j["bufferViews"][a["bufferView"]]
    bas = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    n = {"VEC3": 3, "SCALAR": 1}[a["type"]]
    tur = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}[a["componentType"]]
    adim = bv.get("byteStride", 0)
    if adim and adim != np.dtype(tur).itemsize * n:
        ham = np.frombuffer(veri, np.uint8, adim * a["count"], bas).reshape(a["count"], adim)
        dizi = ham[:, :np.dtype(tur).itemsize * n].copy().view(tur)
    else:
        dizi = np.frombuffer(veri, tur, a["count"] * n, bas)
    return dizi.reshape(-1, n) if n > 1 else dizi


def dugum_matrisi(n):
    if "matrix" in n:
        return np.array(n["matrix"], float).reshape(4, 4).T
    m = np.eye(4)
    if "scale" in n:
        m = np.diag(list(n["scale"]) + [1.0])
    if "rotation" in n:
        x, y, z, w = n["rotation"]
        r = np.eye(4)
        r[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
        m = r @ m
    if "translation" in n:
        t = np.eye(4)
        t[:3, 3] = n["translation"]
        m = t @ m
    return m


def ucgenleri_topla(j, veri):
    """GLB sahnesini dolaşır; [(parça türü, malzeme no, noktalar mm (n,3,3))] ve gövdesi olan eleman sayısını döndürür."""
    parcalar, elemanlar = [], set()

    def gez(i, m, ust_ad):
        n = j["nodes"][i]
        m = m @ dugum_matrisi(n)
        ad = n.get("name", "")
        if "mesh" in n:
            ag = j["meshes"][n["mesh"]]
            parca = None if ust_ad else next((p for p in KART_PARCALARI if ag.get("name", "").endswith("_" + p)), None)
            if ust_ad:
                elemanlar.add(ust_ad)
            for pr in ag["primitives"]:
                if pr.get("mode", 4) != 4:
                    continue
                p = erisim(j, veri, pr["attributes"]["POSITION"]).astype(float)
                p = (p @ m[:3, :3].T + m[:3, 3]) * 1000.0
                ix = erisim(j, veri, pr["indices"]).astype(np.int64) if "indices" in pr else np.arange(len(p))
                parcalar.append((parca or "eleman", pr.get("material", -1), p[ix.reshape(-1, 3)]))
        for c in n.get("children", []):
            gez(c, m, ad if "children" in n and not ad.startswith("=>") else ust_ad)

    for kok in j["scenes"][j.get("scene", 0)]["nodes"]:
        gez(kok, np.eye(4), "")
    return parcalar, len(elemanlar)


def malzeme(j, no, parca):
    """(renk rgba, metal mi, pürüz) döndürür. Eleman gövdelerinde dosya yalnız renk verir; yalıtkan sayılır."""
    pbr = (j["materials"][no].get("pbrMetallicRoughness", {}) if no >= 0 else {})
    r = list(pbr.get("baseColorFactor", [0.6, 0.6, 0.6, 1.0]))
    if parca == "eleman":
        r = [round(c * 24) / 24 for c in r[:3]] + [1.0]      # çok yakın renkler tek grupta toplansın
        return tuple(r), 0, 0.5
    if parca == "silkscreen":
        r[3] = 1.0
    return tuple(round(c, 3) for c in r), int(pbr.get("metallicFactor", 0) > 0.5), round(pbr.get("roughnessFactor", 0.6), 2)


def katman_ac(y, alt, ust):
    """Kart yüzeyine yapışık katmanları (bakır, maske, serigrafi) yüzeyden uzaklaştırır; üstündeki her şey o kadar kayar."""
    k, b = KATMAN_ACMA, KATMAN_BANDI
    y = y.copy()
    u = y > ust
    y[u] = np.where(y[u] - ust < b, ust + (y[u] - ust) * k, y[u] + b * (k - 1))
    a = y < alt
    y[a] = np.where(alt - y[a] < b, alt - (alt - y[a]) * k, y[a] - b * (k - 1))
    return y


def degisken_uzunluk(d):
    """Negatif olmayan tam sayıları 7 bitlik parçalarla (küçük sayı tek bayt) yazar."""
    d = d.astype(np.uint32)
    parca = [(d >> (7 * i)) & 0x7F for i in range(5)]
    uzunluk = np.ones(len(d), np.int64)
    for i in range(1, 5):
        uzunluk[d >= (1 << (7 * i))] = i + 1
    son = np.cumsum(uzunluk)
    cikti = np.zeros(int(son[-1]) if len(d) else 0, np.uint8)
    bas = son - uzunluk
    for i in range(5):
        sec = uzunluk > i
        devam = (uzunluk[sec] > i + 1).astype(np.uint8) << 7
        cikti[bas[sec] + i] = parca[i][sec].astype(np.uint8) | devam
    return cikti.tobytes()


def grup_kodla(p16, ucgen):
    """Noktaları ilk kullanılış sırasına dizer; konumları fark + zikzak, dizinleri 'en son yeni noktaya uzaklık' olarak yazar."""
    duz = ucgen.reshape(-1)
    essiz, ilk = np.unique(duz, return_index=True)
    sira = np.argsort(ilk, kind="stable")
    yeni_no = np.empty(len(p16), np.int64)
    yeni_no[essiz[sira]] = np.arange(len(essiz))
    p = p16[essiz[sira]].astype(np.int64)
    duz = yeni_no[duz]
    govde = b""
    for eksen in range(3):
        f = np.diff(p[:, eksen], prepend=0)
        f = ((f + 32768) & 0xFFFF) - 32768                 # 16 bitlik işaretli fark
        z = ((f << 1) ^ (f >> 15)) & 0xFFFF                # zikzak: küçük farklar küçük sayı olur
        govde += (z & 0xFF).astype(np.uint8).tobytes() + (z >> 8).astype(np.uint8).tobytes()
    yeni = np.zeros(len(duz), np.int64)
    yeni[np.sort(ilk)] = 1
    sinir = np.cumsum(yeni) - yeni                         # o ana kadar görülen nokta sayısı
    govde += degisken_uzunluk(sinir - duz)                 # yeni nokta 0, eski nokta >= 1
    return len(p), govde


def model_uret(glb_yolu):
    j, veri = glb_oku(glb_yolu)
    parcalar, govdeli = ucgenleri_topla(j, veri)
    govde_y = np.concatenate([u[:, :, 1].reshape(-1) for parca, _, u in parcalar if parca == "PCB"] or [np.zeros(1)])
    alt, ust = float(govde_y.min()), float(govde_y.max())
    orta = (alt + ust) / 2
    ham_gruplar = {}
    for parca, no, u in parcalar:
        ham_gruplar.setdefault((parca, no), []).append(u)
    gruplar = {}
    for (parca, no), liste in ham_gruplar.items():
        u = np.concatenate(liste)
        if parca in ("copper", "via", "pad"):
            # Yalnız dışa bakan yatay yüz tutulur: üst yüzdeki bakırın en üstü, alt yüzdekinin en altı.
            # Yan duvarlar (35 mikron), kartın içinde kalan yüzler ve delik çeperleri atılır.
            n = np.cross(u[:, 1] - u[:, 0], u[:, 2] - u[:, 0])
            boy = np.linalg.norm(n, axis=1)
            yatay = np.abs(np.divide(n[:, 1], boy, out=np.zeros(len(n)), where=boy > 0)) > 0.9
            y = u[:, :, 1].mean(axis=1)
            tut = np.zeros(len(u), bool)
            ustte = yatay & (y > orta)
            altta = yatay & (y <= orta)
            if ustte.any():
                tut |= ustte & (y > y[ustte].max() - 0.004)
            if altta.any():
                tut |= altta & (y < y[altta].min() + 0.004)
            u = u[tut]
        if not len(u):
            continue
        anahtar = (TUR.get(parca, "eleman"),) + malzeme(j, no, parca)
        gruplar.setdefault(anahtar, []).append(u)

    for anahtar in gruplar:
        u = np.concatenate(gruplar[anahtar]).reshape(-1, 3)
        u[:, 1] = katman_ac(u[:, 1], alt, ust)
        gruplar[anahtar] = u
    en_az = np.min([u.min(axis=0) for u in gruplar.values()], axis=0)
    en_cok = np.max([u.max(axis=0) for u in gruplar.values()], axis=0)
    adim = float((en_cok - en_az).max()) / 65535.0
    baslik = {"adim": adim, "kose": [float(c) for c in en_az], "boyut": [float(c) for c in (en_cok - en_az)],
              "kart": [alt, ust], "gruplar": []}
    govde, toplam = [], 0
    sira = {"govde": 0, "bakir": 1, "ped": 2, "eleman": 3, "yazi": 4, "maske": 5}
    for anahtar in sorted(gruplar, key=lambda a: (sira[a[0]], a[1:])):
        u = gruplar[anahtar]
        q = np.clip(np.rint((u - en_az) / adim), 0, 65535).astype(np.int64)
        kod = (q[:, 0] << 32) | (q[:, 1] << 16) | q[:, 2]
        essiz, ters = np.unique(kod, return_inverse=True)
        ucgen = ters.reshape(-1, 3)
        ucgen = ucgen[(ucgen[:, 0] != ucgen[:, 1]) & (ucgen[:, 1] != ucgen[:, 2]) & (ucgen[:, 0] != ucgen[:, 2])]
        if not len(ucgen):
            continue
        p16 = np.stack([essiz >> 32, (essiz >> 16) & 0xFFFF, essiz & 0xFFFF], axis=1)
        nokta, veri_g = grup_kodla(p16, ucgen)
        baslik["gruplar"].append({"tur": anahtar[0], "renk": list(anahtar[1]), "metal": anahtar[2], "puruz": anahtar[3],
                                  "nokta": nokta, "ucgen": int(len(ucgen)), "bayt": len(veri_g)})
        govde.append(veri_g)
        toplam += len(ucgen)
    bj = json.dumps(baslik, separators=(",", ":")).encode()
    ham = b"OPK1" + struct.pack("<I", len(bj)) + bj + b"".join(govde)
    return ham, toplam, govdeli


def readme_bilgisi(klasor):
    """Kart ölçüsü, katman sayısı ve denetim durumunu kartın README dosyasındaki 'Kart çizimi (otomatik)' bölümünden okur."""
    yol = os.path.join(KOK, "01_DONANIM", klasor, "README.md")
    b = {}
    if not os.path.exists(yol):
        return b
    t = open(yol, encoding="utf-8").read()
    i = t.find("## Kart çizimi (otomatik)")
    if i < 0:
        return b
    t = t[i:]
    m = re.search(r"\*\*Kart:\*\*\s*(\d+)\s*x\s*(\d+)\s*mm,\s*(\d+)\s*katman.*?(\d+)\s*eleman", t)
    if m:
        b.update(en=int(m.group(1)), boy=int(m.group(2)), katman=int(m.group(3)), eleman=int(m.group(4)))
    m = re.search(r"\*\*Denetim[^\n]*?(\d+)\s*ihlal[^\n]*?(\d+)\s*bağlanmamış uç", t)
    if m:
        ihlal, eksik = int(m.group(1)), int(m.group(2))
        if eksik:
            b["durum"], b["uyari"] = "Tamamlanmadı: %d bağlantı eksik" % eksik, 1
        elif ihlal:
            b["durum"], b["uyari"] = "Tamamlanmadı: %d kural ihlali" % ihlal, 1
        else:
            b["durum"] = "DRC temiz"
    if "BU KART BU HÂLİYLE ÜRETİLİP GÜÇ VERİLMEZ" in t:
        b["durum"], b["uyari"] = "Taslak — yüksek akım yolları yetersiz, bu hâliyle üretilmez", 1
    return b


def kart(kimlik, klasor, kok, ad):
    pcb = os.path.join(KOK, "01_DONANIM", klasor, "kicad", kok + ".kicad_pcb")
    if not os.path.exists(pcb):
        return None
    ortam = dict(os.environ)
    for surum in ("10", "9"):
        ortam.setdefault("KICAD%s_3DMODEL_DIR" % surum, "/usr/share/kicad/3dmodels")
    with tempfile.TemporaryDirectory() as gecici:
        glb = os.path.join(gecici, kimlik + ".glb")
        s = subprocess.run(["kicad-cli", "pcb", "export", "glb", "-f", "--subst-models", "--include-tracks", "--include-pads",
                            "--include-zones", "--include-silkscreen", "--include-soldermask", "-o", glb, pcb],
                           capture_output=True, text=True, env=ortam, cwd=gecici)
        if s.returncode or not os.path.exists(glb):
            raise SystemExit("kicad-cli GLB üretemedi (%s):\n%s" % (klasor, (s.stdout + s.stderr)[-2000:]))
        ham, ucgen, govdeli = model_uret(glb)
    metin = base64.b64encode(zlib.compress(ham, 9)).decode().translate(str.maketrans(*HARF_DEGISIMI))
    os.makedirs(CIKTI, exist_ok=True)
    with open(os.path.join(CIKTI, kimlik + ".js"), "w", encoding="utf-8", newline="\n") as f:
        f.write("window.OPERFLY_KART_YUKLE(%s,%s);\n" % (json.dumps(kimlik), json.dumps(metin)))
    b = {"ad": ad, "dosya": "kart/%s.js" % kimlik, "ucgen": ucgen, "govdeli": govdeli}
    b.update(readme_bilgisi(klasor))
    if "eleman" not in b:
        b["eleman"] = len(re.findall(r"^\t\(footprint ", open(pcb, encoding="utf-8").read(), re.M))
    return b


def main():
    secim = set(a.upper() for a in sys.argv[1:])
    bilinen = set(k[1] for k in KARTLAR)
    if secim - bilinen:
        raise SystemExit("Bilinmeyen kart: %s (bilinenler: %s)" % (", ".join(sorted(secim - bilinen)), ", ".join(sorted(bilinen))))
    os.makedirs(CIKTI, exist_ok=True)
    eski = {}
    liste_js = os.path.join(CIKTI, "liste.js")
    if os.path.exists(liste_js):
        eski = json.loads(open(liste_js, encoding="utf-8").read().split("=", 1)[1].rstrip().rstrip(";"))
    sonuc = {}
    for kimlik, klasor, kok, ad in KARTLAR:
        if secim and klasor not in secim and kimlik in eski and os.path.exists(os.path.join(CIKTI, kimlik + ".js")):
            sonuc[kimlik] = eski[kimlik]
            continue
        k = kart(kimlik, klasor, kok, ad)
        if k:
            sonuc[kimlik] = k
            print("%-14s %7d üçgen, %3d/%3d eleman gövdeli, %5d kB  %s" % (
                klasor, k["ucgen"], k["govdeli"], k.get("eleman", 0),
                os.path.getsize(os.path.join(CIKTI, kimlik + ".js")) // 1024, k.get("durum", "")), flush=True)
        else:
            print("%-14s kart dosyası yok, atlandı" % klasor, flush=True)
    with open(liste_js, "w", encoding="utf-8", newline="\n") as f:
        f.write("window.OPERFLY_KART=" + json.dumps(sonuc, ensure_ascii=False) + ";\n")
    print("yazıldı: %s (%d kart)" % (os.path.relpath(liste_js, KOK), len(sonuc)))


if __name__ == "__main__":
    main()
