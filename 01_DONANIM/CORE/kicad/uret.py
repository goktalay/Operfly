"""Operfly Core şematiğini üretir. Çalıştırma: depo kökünden `python 01_DONANIM/CORE/kicad/uret.py`.

Kaynaklar: bu dosya ve ../pin_atamalari.csv. Çıktılar (*.kicad_sch) elle düzenlenmez.
"""
import csv
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from sema_uret import Sema, kicad_sembol_dizini  # noqa: E402

ORTAK = os.path.join(KOK, "01_DONANIM", "ORTAK_KUTUPHANE", "semboller", "operfly.kicad_sym")
BURASI = os.path.dirname(os.path.abspath(__file__))
KICAD = kicad_sembol_dizini()
P, T = "operfly_core", "2026-11-15"

kok = Sema(P, "Operfly Core", kagit="A3", tarih=T)
kok.metin("Operfly Core - ucus kontrol karti (OPFCOR)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/CORE/kicad/uret.py", 25.4, 33.02, 1.6)

# --- Sayfa 2: omurga portlari -------------------------------------------------
om = Sema(P, "Operfly Core - omurga portlari", kagit="A3", tarih=T, ust=kok, ad="Omurga", genel_etiket=True)
kok.alt_sayfa(om, "omurga.kicad_sch", 25.4, 50.8)
bus = om.kutuphane("operfly", ORTAK, "Operfly_Bus_20")
# Port 1: tam omurga. Core 100 Mbit calisir: yalnizca A ve B ciftleri kullanilir.
port1 = {"+12V": "+12V_BUS1", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L",
         "PPS": "PPS_BUS", "ETH_A+": "ETH_TX+", "ETH_A-": "ETH_TX-", "ETH_B+": "ETH_RX+", "ETH_B-": "ETH_RX-"}
# Port 2: yedek guc ve CAN; Ethernet ve PPS bagli degil (karar: 15 Kasim 2026).
port2 = {"+12V": "+12V_BUS2", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L"}
om.koy(bus, "J1", "Operfly Bus 1", 80, 90, port1)
om.koy(bus, "J2", "Operfly Bus 2 (yedek)", 190, 90, port2)
om.metin("Port 1: tam omurga. Port 2: yedek guc ve CAN.", 40, 40)
om.yaz(os.path.join(BURASI, "omurga.kicad_sch"))

# --- Sayfa 3: islemci ---------------------------------------------------------
mcu = Sema(P, "Operfly Core - islemci (STM32H753IIK6)", kagit="A1", tarih=T, ust=kok, ad="Islemci", genel_etiket=True)
kok.alt_sayfa(mcu, "islemci.kicad_sch", 101.6, 50.8)
h7 = mcu.kutuphane("MCU_ST_STM32H7", os.path.join(KICAD, "MCU_ST_STM32H7.kicad_sym"), "STM32H753IIKx")
adlar = {}
for no, ad, _x, _y, _a in mcu.pinler[h7]:
    adlar.setdefault(ad.split("-")[0] if ad.startswith("P") else ad, []).append(no)
aglar = {}
for satir in csv.DictReader(open(os.path.join(BURASI, "..", "pin_atamalari.csv"), encoding="utf-8"), delimiter=";"):
    (top,) = adlar[satir["pin"]]
    aglar[top] = satir["sinyal"]
guc = {"VDD": "+3V3", "VDD33_USB": "+3V3", "VSS": "GND", "VSSA": "GND", "VREF-": "GND", "VDDA": "+3V3A", "VREF+": "VREF",
       "VBAT": "VBAT", "NRST": "MCU_NRST", "BOOT0": "MCU_BOOT0",
       "PDR_ON": "+3V3"}   # PDR_ON: dahili besleme gozetimi acik
for ad, ag in guc.items():
    for top in adlar[ad]:
        aglar[top] = ag
for i, top in enumerate(sorted(adlar["VCAP"]), 1):
    aglar[top] = "VCAP%d" % i   # her VCAP pinine ayri kondansator
mcu.koy(h7, "U1", "STM32H753IIK6", 420, 300, aglar, footprint="Package_BGA:UFBGA-201_10x10mm_Layout15x15_P0.65mm")
mcu.metin("Pin atamalari: 01_DONANIM/CORE/pin_atamalari.csv. Etiketsiz pinler bostur.", 40, 30)
mcu.yaz(os.path.join(BURASI, "islemci.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_core.kicad_sch"))
