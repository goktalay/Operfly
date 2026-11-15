"""Kart şematiklerinde ortak kullanılan yardımcılar: referans sayacı, sembol yükleme, eleman dizme.

Yeni kartların `kicad/uret.py` dosyaları bunu kullanır (Core kendi kopyasını taşır).
"""
import os

from sema_uret import kicad_sembol_dizini

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORTAK = os.path.join(KOK, "01_DONANIM", "ORTAK_KUTUPHANE", "semboller", "operfly.kicad_sym")
ORTAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/semboller/operfly.kicad_sym"
C0402, C0603, C0805, C1206 = ("Capacitor_SMD:C_%s" % x for x in ("0402_1005Metric", "0603_1608Metric", "0805_2012Metric", "1206_3216Metric"))
R0402 = "Resistor_SMD:R_0402_1005Metric"
XAL = "Inductor_SMD:L_Coilcraft_XAL4020-XXX"


class Izgara:
    """Küçük elemanları satır satır dizer."""

    def __init__(self, x, y, dx=22.86, dy=27.94, sutun=10):
        self.x0, self.y0, self.dx, self.dy, self.sutun, self.i = x, y, dx, dy, sutun, 0

    def yer(self):
        x, y = self.x0 + (self.i % self.sutun) * self.dx, self.y0 + (self.i // self.sutun) * self.dy
        self.i += 1
        return x, y

    def satir(self):
        self.i = ((self.i + self.sutun - 1) // self.sutun) * self.sutun


class Kart:
    def __init__(self, proje, tarih):
        self.P, self.T, self.sayac, self.kicad = proje, tarih, {}, kicad_sembol_dizini()

    def ref(self, onek):
        self.sayac[onek] = self.sayac.get(onek, 0) + 1
        return "%s%d" % (onek, self.sayac[onek])

    def lib(self, sema, ad):
        """'Kutuphane:Sembol' adını yükler; 'operfly:' ortak kütüphanedir."""
        k, s = ad.split(":", 1)
        if ad not in sema.lib:
            sema.kutuphane(k, ORTAK if k == "operfly" else os.path.join(self.kicad, k + ".kicad_sym"), s)
        return ad

    def koy(self, sema, sembol, onek, deger, x, y, aglar, fp, dnp=False):
        r = self.ref(onek)
        sema.koy(self.lib(sema, sembol), r, deger, x, y, aglar, footprint=fp, dnp=dnp)
        return r

    def iki(self, sema, g, sembol, onek, deger, a, b, fp, dnp=False):
        """İki uçlu eleman: 1. uç a ağına, 2. uç b ağına. dnp: karta dizilmez (yeri hazır)."""
        x, y = g.yer()
        return self.koy(sema, sembol, onek, deger + (" DNP" if dnp else ""), x, y, {"1": a, "2": b}, fp, dnp)

    def C(self, sema, g, deger, a, b="GND", fp=C0402, dnp=False):
        return self.iki(sema, g, "Device:C", "C", deger, a, b, fp, dnp)

    def R(self, sema, g, deger, a, b, fp=R0402, dnp=False):
        return self.iki(sema, g, "Device:R", "R", deger, a, b, fp, dnp)

    def parca(self, sema, g, sembol, onek, deger, aglar, fp, bosluk=1, dx=10):
        """Çok uçlu eleman; ızgarada 1 + bosluk hücre kaplar."""
        x, y = g.yer()
        for _ in range(bosluk):
            g.yer()
        return self.koy(sema, sembol, onek, deger, x + dx, y, aglar, fp)

    def bayrak(self, sema, g, ag):
        sema.bayrak(ag, *g.yer(), self.kicad)

    def olcum_noktasi(self, sema, g, ag):
        x, y = g.yer()
        return self.koy(sema, "Connector:TestPoint", "TP", ag, x, y, {"1": ag}, "TestPoint:TestPoint_Pad_D1.0mm")
