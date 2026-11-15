#!/usr/bin/env python3
"""Üçüncü taraf adlarının dokümantasyon dışında geçmediğini denetler.

Kullanım: python3 10_ORTAK_ARACLAR/marka_denetle.py [kök_dizin]
Bulgu varsa 1 ile çıkar. Yasak sözcükler 13_DOKUMANTASYON/marka_yasak_listesi.txt dosyasından okunur.
İzinli yerler: 13_DOKUMANTASYON/ ve '.marka_muaf' dosyası içeren klasörler (lisans başlıkları
korunması gereken üçüncü taraf kaynak ağaçları).
"""
import os
import re
import sys

kok = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
liste = os.path.join(kok, "13_DOKUMANTASYON", "marka_yasak_listesi.txt")
with open(liste, encoding="utf-8") as f:
    sozcukler = [s.strip() for s in f if s.strip() and not s.startswith("#")]
desen = re.compile("|".join(re.escape(s) for s in sozcukler), re.IGNORECASE)
atla = {".git", "13_DOKUMANTASYON", "node_modules", "__pycache__"}
bulgu = 0
for dizin, altlar, dosyalar in os.walk(kok):
    altlar[:] = [a for a in altlar if a not in atla]
    if ".marka_muaf" in dosyalar:
        altlar[:] = []
        continue
    goreli = os.path.relpath(dizin, kok)
    for ad in altlar + dosyalar:
        if desen.search(ad):
            print(f"AD   {os.path.join(goreli, ad)}")
            bulgu += 1
    for ad in dosyalar:
        yol = os.path.join(dizin, ad)
        try:
            with open(yol, encoding="utf-8") as f:
                for no, satir in enumerate(f, 1):
                    if desen.search(satir):
                        print(f"METIN {os.path.relpath(yol, kok)}:{no}: {satir.strip()[:100]}")
                        bulgu += 1
        except (UnicodeDecodeError, OSError):
            continue
print(f"{bulgu} bulgu")
sys.exit(1 if bulgu else 0)
