"""Operfly Core şematiğini üretir. Çalıştırma: depo kökünden `python 01_DONANIM/CORE/kicad/uret.py`."""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from sema_uret import Sema  # noqa: E402

ORTAK = os.path.join(KOK, "01_DONANIM", "ORTAK_KUTUPHANE", "semboller", "operfly.kicad_sym")
BURASI = os.path.dirname(os.path.abspath(__file__))

s = Sema("operfly_core", "Operfly Core - omurga portlari", kagit="A3", rev="A", tarih="2026-11-15")
bus = s.kutuphane("operfly", ORTAK, "Operfly_Bus_20")

# Port 1: tam omurga (guc + iki CAN FD + PPS + Ethernet). Core 100 Mbit calisir: yalnizca A ve B ciftleri kullanilir.
port1 = {"+12V": "+12V_BUS1", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L",
         "PPS": "PPS_BUS", "ETH_A+": "ETH_TX+", "ETH_A-": "ETH_TX-", "ETH_B+": "ETH_RX+", "ETH_B-": "ETH_RX-"}
# Port 2: yedek guc ve CAN; Ethernet ve PPS bagli degil.
port2 = {"+12V": "+12V_BUS2", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L"}
s.koy(bus, "J1", "Operfly Bus 1", 80, 90, port1)
s.koy(bus, "J2", "Operfly Bus 2 (yedek)", 190, 90, port2)
s.metin("Operfly Bus portlari - taslak. Port 2 yedek guc ve CAN icindir.", 40, 40)
s.yaz(os.path.join(BURASI, "operfly_core.kicad_sch"))
