"""Operfly Hub kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "en": 180.0, "boy": 130.0,
    "tohum": 1,
    "kenar_bosluk": 2.0, "ic_payi": 1.0,
    "sure_dk": 720,   # yol çiziciye tanınan süre (dakika)
    "katman": 6, "duzlemler": {"In1.Cu": "GND", "In4.Cu": "+3V3"},   # 6 katman: iç 1 toprak, iç 4 +3V3, diğerleri sinyal
    # 12 omurga portu: kuzey ve güney kenarlarında dörder, doğu ve batıda ikişer.
    "kenar": {"J2": ("K", None), "J3": ("K", None), "J4": ("K", None), "J5": ("K", None),
              "J6": ("G", None), "J7": ("G", None), "J8": ("G", None), "J9": ("G", None),
              "J10": ("D", None), "J11": ("D", None), "J12": ("B", None), "J13": ("B", None)},
}
