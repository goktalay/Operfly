"""Septentrio mosaic modül ailesinin (mosaic-X5, mosaic-H; ortak 239 uçlu LGA) pad tablosu.

Kaynak: Septentrio "mosaic Hardware Manual" sürüm 1.11.0, Ek G (Pad List) ve bölüm 4'teki üstten görünüş.
Tablo belgeden betikle çıkarıldı; 239 pad ve dizilim (23 x 23, dıştan üç sıra, A1 yok) sayılarak denetlendi.
Sembol (kutuphane_uret.py) ve ayak izi (ayak_izi_uret.py) bu tabloyu kullanır.
"""
SATIRLAR = "A B C D E F G H J K L M N P R T U V W Y AA AB AC".split()

# ad -> pad numaraları
PADLER = {
    "GND": (
        "A4 A7 A15 A16 A17 A21 A22 A23 B4 B5 B6 B7 B13 B17 B21 C4 "
        "C7 C15 C16 C17 C23 D2 D21 D22 D23 E2 E21 E22 E23 F21 F22 F23 "
        "G2 G21 G23 H21 H22 H23 J21 J22 J23 K2 K21 K22 K23 L21 L22 L23 "
        "M21 M22 N21 N22 P1 P2 P3 P21 P22 R3 R21 R22 T21 T22 T23 U2 "
        "U21 U22 U23 V21 V22 W21 W22 W23 Y2 Y21 Y22 Y23 AA13 AA14 AA15 AA16 "
        "AA17 AA18 AA19 AA20 AA21 AA22 AA23 AB2 AB3 AB4 AB5 AB6 AB8 AB13 AB14 AB15 "
        "AB16 AB17 AB18 AB19 AB20 AB21 AB22 AB23 AC13 AC15 AC18 AC19 AC21 AC22 AC23 "
    ),
    "Reserved_NC": (
        "A9 A13 B3 B9 B10 B11 B12 B14 B15 B22 B23 C2 C3 C5 C6 C8 "
        "C9 C10 C11 C12 C13 C14 C21 C22 F3 G3 G22 H3 J3 N3 R1 T1 "
        "T3 U1 U3 V1 V3 W1 W3 Y3 AA3 AA5 AA6 AA7 AA8 AA9 AA10 AA11 "
        "AA12 AB9 AB10 AB11 AB12 AC1 AC2 AC5 AC9 AC10 AC11 AC12 "
    ),
    "VDD_3V3": "A18 A19 A20 B18 B19 B20 C18 C19 C20",
    "VANT": "P23 R23",
    "1V8_OUT": "AC4",
    "2V8_IN": "M23",
    "2V8_OUT": "N23",
    "ANT_1": "AC20",
    "ANT_2": "V23",
    "CTS1": "E1",
    "CTS2": "J1",
    "CTS3": "N1",
    "EVENTA": "AC6",
    "EVENTB": "AC7",
    "GP1": "AA4",
    "GP2": "L3",
    "GPLED": "A14",
    "GPLED2": "M3",
    "LOGBUTTON": "K3",
    "LOGLED": "B2",
    "MDC": "V2",
    "MDIO": "W2",
    "MODULE_RDY": "A12",
    "ONOFF": "A10",
    "PMIC_ON_REQ": "B16",
    "PPSO": "AC8",
    "REF_I": "AC17",
    "REF_O": "AC16",
    "RMII_CLK": "AA2",
    "RMII_CRSDV": "N2",
    "RMII_RXD0": "R2",
    "RMII_RXD1": "T2",
    "RMII_RXER": "M2",
    "RMII_TXD0": "J2",
    "RMII_TXD1": "H2",
    "RMII_TXEN": "L2",
    "RTC_XTALI": "A3",
    "RTC_XTALO": "A2",
    "RTS1": "C1",
    "RTS2": "G1",
    "RTS3": "L1",
    "RXD1": "B1",
    "RXD2": "F1",
    "RXD3": "K1",
    "RXD4": "D3",
    "Reserved_GND": "AB7",
    "SD1_CLK": "AA1",
    "SD1_CMD": "AB1",
    "SD1_DATA0": "Y1",
    "SYNC": "AC3",
    "TXD1": "D1",
    "TXD2": "H1",
    "TXD3": "M1",
    "TXD4": "E3",
    "USB_DEV_N": "A6",
    "USB_DEV_P": "A5",
    "USB_VBUS1": "A8",
    "VDD_BAT": "B8",
    "VTUNE": "AC14",
    "nRST_IN": "A11",
    "nRST_LAN": "F2",
}
PADLER = {ad: p.split() for ad, p in PADLER.items()}


def konum(pad, adim=1.27):
    """Kart üstünden bakışta pad merkezi (mm; x sağa, y aşağı). A1 sol üstte, sütunlar sağa, satırlar aşağı artar.

    Üreticinin üstten görünüşü (AC üstte, 23. sütun solda) 180 derece döndürülmüş hâlidir; ayna alınmamıştır.
    """
    i = 1 if pad[1].isdigit() else 2
    return (int(pad[i:]) - 12) * adim, (SATIRLAR.index(pad[:i]) - 11) * adim


def denetle():
    tum = [p for ps in PADLER.values() for p in ps]
    assert len(tum) == len(set(tum)) == 239, len(tum)
    beklenen = {"%s%d" % (s, c) for i, s in enumerate(SATIRLAR) for c in range(1, 24) if i < 3 or i >= 20 or c <= 3 or c >= 21} - {"A1"}
    assert set(tum) == beklenen
    assert PADLER["ANT_1"] == ["AC20"] and PADLER["ANT_2"] == ["V23"] and PADLER["Reserved_GND"] == ["AB7"] and PADLER["RTC_XTALI"] == ["A3"]


denetle()
