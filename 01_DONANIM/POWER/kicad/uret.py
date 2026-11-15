"""Operfly Power şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py POWER operfly_power`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import ORTAK_URI, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
k = Kart("operfly_power", "2026-11-15")
kok = Sema(k.P, "Operfly Power", kagit="A3", tarih=k.T)
kok.metin("Operfly Power - guc karti (OPFPWR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/POWER/kicad/uret.py. Guc kati sayfalari henuz cizilmedi (README).", 25.4, 33.02, 1.6)

# Düğüm devresi. Karta ayrılan pinler güç katı çizilince `ek` ile bağlanacak (ölçüm hatları, açma/kapama, arıza girişleri).
dg = dugum_sayfasi(k, kok, BURASI)

kok.yaz(os.path.join(BURASI, "operfly_power.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg], {"operfly": ORTAK_URI})
print("elemanlar:", dict(sorted(k.sayac.items())))
