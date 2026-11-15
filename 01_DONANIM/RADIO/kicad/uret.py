"""Operfly Radio şematiğini üretir. Çalıştırma: depo kökünden `python 10_ORTAK_ARACLAR/kicad/denetle.py RADIO operfly_radio`.

Kaynak bu dosyadır; `*.kicad_sch` çıktıları elle düzenlenmez.
Yapı: düğüm devresi + geniş bant radyo modülü (Microhard pMDDL2450 OEM) + modül beslemeleri (3,3 V ve 5 V) +
Ethernet trafosu (modülün LAN portu omurganın A ve B çiftlerine).
Modülün uç sırası ve çevre devresi üreticinin işletme kılavuzundandır (pMDDL Operating Manual v1.4.2, bölüm 3.1 ve Ek C).
"""
import os
import sys

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(KOK, "10_ORTAK_ARACLAR", "kicad"))
from dugum import dugum_sayfasi  # noqa: E402
from kart import C0603, C0805, C1206, ORTAK_URI, XAL, Izgara, Kart  # noqa: E402
from sema_uret import Sema, kutuphane_tablolari  # noqa: E402

BURASI = os.path.dirname(os.path.abspath(__file__))
AYAK_URI = "${KIPRJMOD}/../../ORTAK_KUTUPHANE/ayak_izleri/operfly_ayak.pretty"
FB0603 = "Inductor_SMD:L_0603_1608Metric"
k = Kart("operfly_radio", "2026-11-15")
kok = Sema(k.P, "Operfly Radio", kagit="A3", tarih=k.T)
kok.metin("Operfly Radio - genis bant baglanti karti (OPFRAD)", 25.4, 25.4, 3.0)
kok.metin("Sematik betikle uretilir: 01_DONANIM/RADIO/kicad/uret.py.", 25.4, 33.02, 1.6)

# Düğüm devresi ve karta ayrılan işlemci pinleri (KiCad pin verisindeki alternatif işlevlerle denetlendi).
EK = {"PA2": "RADIO_RXD", "PA3": "RADIO_TXD",              # USART2_TX -> modul Serial RxD, USART2_RX <- modul Serial TxD
      "PA1": "RADIO_RTS", "PA0": "RADIO_CTS",              # USART2_RTS -> modul RTS (giris), USART2_CTS <- modul CTS (cikis)
      "PB0": "RADIO_NRST", "PB1": "RADIO_CONFIG_N",        # acik kollektor: modulu sifirlar / fabrika ayari ve kurtarma kipi
      "PA4": "RADIO_RF_OFF",                               # 1: verici katinin 5 V beslemesi kapali (sifirlamada acik)
      "PB3": "RADIO_CPU_STATUS",                           # modulun "calisiyor" cikisi
      "PA5": "RADIO_VRF_SENS"}                             # ADC1_IN5: verici besleme gerilimi / 2
dg = dugum_sayfasi(k, kok, BURASI, ek=EK, ethernet=2, ldo33=False)

# --- Radyo: modül, seri arayüz, ışıklar --------------------------------------
rd = Sema(k.P, "Operfly Radio - genis bant radyo modulu ve Ethernet", kagit="A1", tarih=k.T, ust=kok, ad="Radyo", genel_etiket=True)
kok.alt_sayfa(rd, "radyo.kicad_sch", 101.6, 50.8)
rd.metin("GENIS BANT RADYO MODULU (Microhard pMDDL2450 OEM, 2,4 GHz, 2x2 MIMO, 1 W). Uc sirasi uretici kilavuzundan (Tablo 3-3).", 30, 28)
rd.metin("Antenler modulun ustundeki iki U.FL konnektorden kabloyla kasadaki SMA'lara gider; kartta RF hatti yoktur.", 30, 34)
rd.metin("DNC uclari fabrikaya ayrilmis, NC uclari desteklenmiyor: hepsi bos. USB ve ikinci Ethernet portu (WAN) kullanilmiyor.", 30, 40)
rd.metin("Modul yaklasik 7,5 W isi uretir: alt toprak duzlemi karta lehimlenir, ustune sogutucu konur (uretici sarti).", 30, 46)
k.koy(rd, "operfly:pMDDL2450", "U", "pMDDL2450 OEM", 110, 150, {
    "Vcc": "+3V3", "VRF": "+5V_RF", "GND": "GND",
    "Serial_RxD": "RADIO_RXD_M", "Serial_TxD": "RADIO_TXD_M", "Serial_RTS": "RADIO_RTS", "Serial_CTS": "RADIO_CTS",
    "RESET": "RADIO_NRST", "CONFIG": "RADIO_CONFIG_N", "CPU_STATUS_LED": "RADIO_CPU_STATUS",
    "LED_RX": "RADIO_LED_RX", "LED_TX": "RADIO_LED_TX", "ETH0_LINK_LED": "RADIO_ETH_LINK",
    "TX_P0": "RETH_TXP", "TX_N0": "RETH_TXN", "RX_P0": "RETH_RXP", "RX_N0": "RETH_RXN", "ETH_BIAS": "RETH_BIAS"},
    "operfly_ayak:Microhard_pMDDL_OEM")
g = Izgara(50, 250, sutun=10)
for ag, n in (("+3V3", 2), ("+5V_RF", 2)):
    k.C(rd, g, "22u 16V", ag, fp=C1206)
    for _ in range(n):
        k.C(rd, g, "100n", ag)
k.C(rd, g, "100p", "+5V_RF")
g.satir()
rd.metin("SERI ARAYUZ (3,3 V): uretici RxD ve TxD'nin 0R uzerinden disari alinmasini ister (modul kurtarma islemi icin): 0R + olcum noktalari.", 30, 300)
g = Izgara(50, 335, sutun=10)
k.R(rd, g, "0R", "RADIO_RXD", "RADIO_RXD_M"); k.R(rd, g, "0R", "RADIO_TXD", "RADIO_TXD_M")
k.R(rd, g, "10k", "+3V3", "RADIO_NRST"); k.R(rd, g, "10k", "+3V3", "RADIO_CONFIG_N")
for ag in ("RADIO_RXD_M", "RADIO_TXD_M", "RADIO_CONFIG_N", "RADIO_NRST"):
    k.olcum_noktasi(rd, g, ag)
rd.metin("ISIKLAR: modul cikislari en cok 8 mA verir ve acilista belirsizdir; 1 k seri direnc, 10 k asagi cekme.", 30, 385)
g = Izgara(50, 420, sutun=12)
for ag, ad in (("RADIO_CPU_STATUS", "mavi (modul)"), ("RADIO_LED_RX", "yesil (alis)"), ("RADIO_LED_TX", "kirmizi (veris)"), ("RADIO_ETH_LINK", "sari (Ethernet)")):
    k.R(rd, g, "1k", ag, ag + "_A"); k.iki(rd, g, "Device:LED", "D", "LED " + ad, "GND", ag + "_A", "LED_SMD:LED_0603_1608Metric"); k.R(rd, g, "10k", ag, "GND")

rd.metin("ETHERNET (10/100): modulun LAN portu trafo uzerinden omurganin A (gonderme) ve B (alma) ciftlerine. Devre ureticinin ornegidir (Ek C):", 330, 28)
rd.metin("her hatta 49,9 ohm, cift ortasi 100 nF ile topraga; trafonun modul tarafi orta uclari ferrit uzerinden ETH_BIAS'a.", 330, 34)
rd.metin("Kablo tarafi orta uclari 75 ohm + 1 nF / 2 kV ile topraga (Core ile ayni).", 330, 40)
g = Izgara(350, 90, sutun=12)
k.parca(rd, g, "Transformer:PT61017PEL", "T", "PT61017PEL (10/100, 1:1)", {
    "TD+": "RETH_TXP", "TD-": "RETH_TXN", "C_TD": "RETH_CT", "RD+": "RETH_RXP", "RD-": "RETH_RXN", "C_RD": "RETH_CT",
    "TX+": "ETH_A+", "TX-": "ETH_A-", "C_TX": "RETH_CT_A", "RX+": "ETH_B+", "RX-": "ETH_B-", "C_RX": "RETH_CT_B"},
    "Transformer_SMD:Transformer_Ethernet_Bourns_PT61017PEL", bosluk=2, dx=25)
k.R(rd, g, "49R9 1%", "RETH_TXP", "RETH_TERM_TX"); k.R(rd, g, "49R9 1%", "RETH_TXN", "RETH_TERM_TX"); k.C(rd, g, "100n", "RETH_TERM_TX")
k.R(rd, g, "49R9 1%", "RETH_RXP", "RETH_TERM_RX"); k.R(rd, g, "49R9 1%", "RETH_RXN", "RETH_TERM_RX"); k.C(rd, g, "100n", "RETH_TERM_RX")
g.satir()
k.iki(rd, g, "Device:FerriteBead", "FB", "BLM18HD102SN1D", "RETH_BIAS", "RETH_CT", FB0603)
k.C(rd, g, "100n", "RETH_BIAS"); k.C(rd, g, "100n", "RETH_CT")
k.R(rd, g, "75R", "RETH_CT_A", "RETH_BS"); k.R(rd, g, "75R", "RETH_CT_B", "RETH_BS"); k.C(rd, g, "1n 2kV", "RETH_BS", fp=C1206)

# --- Besleme ------------------------------------------------------------------
rd.metin("3,3 V (AP63203, 12 V'tan, 2 A): modulun sayisal kati 0,5 A'ya kadar ceker; dugum islemcisi de bu raydadir. Core'daki devrenin aynisi.", 330, 170)
g = Izgara(350, 205, sutun=12)
k.parca(rd, g, "Regulator_Switching:AP63203WU", "U", "AP63203QWU",
        {"IN": "+12V", "EN": "EN_3V3", "GND": "GND", "SW": "SW_3V3", "BST": "BST_3V3", "FB": "+3V3"}, "Package_TO_SOT_SMD:TSOT-23-6")
k.R(rd, g, "100k", "+12V", "EN_3V3"); k.C(rd, g, "10u 50V", "+12V", fp=C1206); k.C(rd, g, "100n", "BST_3V3", "SW_3V3")
k.iki(rd, g, "Device:L", "L", "3u3 XAL4020-332", "SW_3V3", "+3V3", XAL)
k.C(rd, g, "22u 16V", "+3V3", fp=C1206); k.C(rd, g, "22u 16V", "+3V3", fp=C1206); k.bayrak(rd, g, "+3V3")

rd.metin("5 V VERICI BESLEMESI (AP63201, 12 V'tan, sabit frekansli): verici kati 30 dBm'de ortalama 1,2 A, anlik 1,5 A ceker.", 330, 260)
rd.metin("Ayri regulator: verici darbeleri dugumun 5 V rayini (CAN) sarsmaz; islemci RADIO_RF_OFF = 1 ile vericiyi susturabilir.", 330, 266)
rd.metin("Besleme sifirlamada ACIKTIR. Cikis = 0,8 V x (1 + 158k / 30k1) = 5,0 V (uretici ornek devresi).", 330, 272)
g = Izgara(350, 310, sutun=12)
k.parca(rd, g, "Regulator_Switching:AP63201WU", "U", "AP63201WU",
        {"IN": "+12V", "EN": "EN_RF", "GND": "GND", "SW": "SW_RF", "BST": "BST_RF", "FB": "FB_RF"}, "Package_TO_SOT_SMD:TSOT-23-6")
k.R(rd, g, "100k", "+12V", "EN_RF"); k.C(rd, g, "10u 50V", "+12V", fp=C1206); k.C(rd, g, "100n", "BST_RF", "SW_RF")
k.iki(rd, g, "Device:L", "L", "10u (Isat >= 3 A)", "SW_RF", "+5V_RF", "Inductor_SMD:L_Coilcraft_XAL5030-XXX")
k.C(rd, g, "22u 16V", "+5V_RF", fp=C1206); k.C(rd, g, "22u 16V", "+5V_RF", fp=C1206); k.bayrak(rd, g, "+5V_RF")
g.satir()
k.R(rd, g, "158k 1%", "+5V_RF", "FB_RF"); k.R(rd, g, "30k1 1%", "FB_RF", "GND"); k.C(rd, g, "100p", "+5V_RF", "FB_RF")
x, y = g.yer()
k.koy(rd, "Transistor_FET:2N7002", "Q", "2N7002", x, y, {"D": "EN_RF", "S": "GND", "G": "RADIO_RF_OFF"}, "Package_TO_SOT_SMD:SOT-23")
k.R(rd, g, "100k", "RADIO_RF_OFF", "GND")
k.R(rd, g, "10k 1%", "+5V_RF", "RADIO_VRF_SENS"); k.R(rd, g, "10k 1%", "RADIO_VRF_SENS", "GND"); k.C(rd, g, "100n", "RADIO_VRF_SENS")
rd.yaz(os.path.join(BURASI, "radyo.kicad_sch"))

kok.yaz(os.path.join(BURASI, "operfly_radio.kicad_sch"))
kutuphane_tablolari(BURASI, [kok, dg, rd], {"operfly": ORTAK_URI, "operfly_ayak": AYAK_URI})
print("yazildi: operfly_radio (kok + 2 sayfa)")
