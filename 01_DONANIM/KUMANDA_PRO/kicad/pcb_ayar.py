"""Kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "en": 195.0, "boy": 140.0,
    "tohum": 1,
    "kenar_bosluk": 2.0, "ic_payi": 1.0,
    "sure_dk": 300,   # yol çiziciye tanınan süre (dakika)
    "katman": 6, "duzlemler": {"In1.Cu": "GND", "In4.Cu": "+3V3"},   # 6 katman: iç 1 toprak, iç 4 +3V3, diğerleri sinyal
    # Jetson soketi ve M.2 yuvası kartın içinde kalır (modüller kartın üstüne yatar).
    "ic": ["J8", "J9"],
}
