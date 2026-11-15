"""Bir kartın şematiğini üretir, güncel KiCad biçimine çevirir, elektrik denetimini (ERC) çalıştırır ve PDF çıkarır.

Kullanım (depo kökünden): python 10_ORTAK_ARACLAR/kicad/denetle.py CORE operfly_core
Çıktılar out/ klasörüne yazılır: <kart>_erc.rpt, <kart>.pdf
"""
import collections
import glob
import os
import re
import subprocess
import sys


def kicad_cli():
    adaylar = sorted(glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "KiCad", "*", "bin", "kicad-cli.exe")), reverse=True)
    adaylar += sorted(glob.glob(r"C:\Program Files\KiCad\*\bin\kicad-cli.exe"), reverse=True) + ["kicad-cli"]
    for a in adaylar:
        if a == "kicad-cli" or os.path.isfile(a):
            return a


def main():
    kart, kok = sys.argv[1], sys.argv[2]
    d = os.path.join("01_DONANIM", kart, "kicad")
    cli = kicad_cli()
    os.makedirs("out", exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(d, "uret.py")], capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        sys.exit(r.returncode)
    for f in sorted(glob.glob(os.path.join(d, "*.kicad_sch"))):
        subprocess.run([cli, "sch", "upgrade", f], capture_output=True)
    rapor = os.path.join("out", kart.lower() + "_erc.rpt")
    subprocess.run([cli, "sch", "erc", "--severity-all", "-o", rapor, os.path.join(d, kok + ".kicad_sch")], capture_output=True)
    metin = open(rapor, encoding="utf-8").read()
    turler = collections.Counter(re.findall(r"^\[(\w+)\]", metin, re.M))
    hata = len(re.findall(r"; error", metin))
    uyari = len(re.findall(r"; warning", metin))
    print("ERC: %d hata, %d uyari" % (hata, uyari))
    for t, n in turler.most_common():
        print("   %-28s %d" % (t, n))
    subprocess.run([cli, "sch", "export", "pdf", "-o", os.path.join("out", kart.lower() + ".pdf"), os.path.join(d, kok + ".kicad_sch")], capture_output=True)
    sys.exit(1 if hata else 0)


if __name__ == "__main__":
    main()
