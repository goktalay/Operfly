"""Operfly Pilot 12 ana kartının şematiğini üretir.
Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_12 operfly_pilot12`.

Kaynak bu dosya ve ortak bölümdür (`10_ORTAK_ARACLAR/kicad/kumanda_ana.py`); `*.kicad_sch` çıktıları elle düzenlenmez.
Pilot 12 ortak bölümün tamamıdır, ek sayfası yoktur. Devre açıklamaları ve veri sayfası listesi ortak bölümün başındadır.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from kumanda_ana import KUTUPHANELER, ana_kart  # noqa: E402
from sema_uret import kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k, kok, sayfalar = ana_kart("operfly_pilot12", "Pilot 12", "OPFK12", "KUMANDA_12", BURASI)
kok.yaz(os.path.join(BURASI, "operfly_pilot12.kicad_sch"))
kutuphane_tablolari(BURASI, [kok] + sayfalar, KUTUPHANELER)
print("yazildi: operfly_pilot12 (kok + 2 sayfa)")
