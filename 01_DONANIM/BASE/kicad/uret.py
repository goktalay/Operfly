"""Operfly Base (RTK baz istasyonu) şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py BASE operfly_base`.

Kaynak bu dosya ve ortak bölümdür (`10_ORTAK_ARACLAR/kicad/nav_ana.py`); `*.kicad_sch` çıktıları elle düzenlenmez.
Nav ve Base aynı devreyi paylaşır: Base'te pusula yoktur, dış besleme girişi vardır. Devre açıklamaları ortak bölümdedir.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from nav_ana import KUTUPHANELER, nav_kart  # noqa: E402
from sema_uret import kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k, kok, sayfalar = nav_kart("operfly_base", "Base", "OPFBAS", "BASE", BURASI, baz=True)
kok.yaz(os.path.join(BURASI, "operfly_base.kicad_sch"))
kutuphane_tablolari(BURASI, [kok] + sayfalar, KUTUPHANELER)
print("yazildi: operfly_base (kok + 3 sayfa)")
