"""Pin atamalarını işlemcinin KiCad sembolündeki gerçek pin yeteneklerine karşı doğrular
ve okunabilir pin haritası üretir.

Kullanım: python pin_dogrula.py <pinler.json> <pin_atamalari.csv> <PIN_HARITASI.md> "<başlık>"
"""
import csv
import json
import sys


def main():
    pj, pc, cikti, baslik = sys.argv[1:5]
    veri = json.load(open(pj, encoding="utf-8"))
    pinler = veri["pinler"]
    satirlar = list(csv.DictReader(open(pc, encoding="utf-8"), delimiter=";"))
    hatalar, kullanilan = [], {}
    for s in satirlar:
        pin, islev = s["pin"], s["islev"]
        # KiCad bazı pin adlarını "PH0-OSC_IN" biçiminde yazar
        aday = [k for k in pinler if k == pin or k.startswith(pin + "-") or k.startswith(pin + "/")]
        if not aday:
            hatalar.append("%s: %s pini bu kılıfta yok" % (s["sinyal"], pin))
            continue
        ad = aday[0]
        s["_top"] = ", ".join(pinler[ad]["numaralar"])
        if pin in kullanilan:
            hatalar.append("%s: %s pini zaten %s için kullanılıyor" % (s["sinyal"], pin, kullanilan[pin]))
        kullanilan[pin] = s["sinyal"]
        if islev != "GPIO" and islev not in pinler[ad]["alternatifler"]:
            benzer = [a for a in pinler[ad]["alternatifler"] if islev.split("_")[0][:4] in a]
            hatalar.append("%s: %s pininde %s işlevi yok; benzerleri: %s" % (s["sinyal"], pin, islev, benzer or pinler[ad]["alternatifler"]))
    if hatalar:
        print("HATA (%d):" % len(hatalar))
        for h in hatalar:
            print(" -", h)
        sys.exit(1)
    io = sorted(k for k in pinler if k[:1] == "P" and k[1:2].isalpha() and k[2:3].isdigit())
    bos = [k for k in io if k.split("-")[0].split("/")[0] not in kullanilan]
    with open(cikti, "w", encoding="utf-8", newline="\n") as f:
        f.write("# %s\n\n" % baslik)
        f.write("Bu dosya `pin_atamalari.csv` dosyasından `10_ORTAK_ARACLAR/kicad/pin_dogrula.py` ile üretilir; elle düzenlemeyin.\n")
        f.write("Her atama, KiCad kütüphanesindeki `%s` sembolünün pin işlevlerine karşı doğrulanmıştır.\n\n" % veri["sembol"])
        f.write("- Kılıf: `%s`\n- Atanan pin: %d\n- Boş kalan G/Ç pini: %d\n\n" % (veri["footprint"], len(kullanilan), len(bos)))
        grup = None
        for s in satirlar:
            if s["grup"] != grup:
                grup = s["grup"]
                f.write("\n## %s\n\n| Sinyal | Pin | Top | İşlev | Not |\n|---|---|---|---|---|\n" % grup)
            f.write("| %s | %s | %s | %s | %s |\n" % (s["sinyal"], s["pin"], s["_top"], s["islev"], s["not"]))
        f.write("\n## Boş pinler\n\n%s\n" % ", ".join(bos))
    print("TAMAM: %d atama doğrulandı, %d G/Ç pini boş" % (len(satirlar), len(bos)))


if __name__ == "__main__":
    main()
