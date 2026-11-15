"""Kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "en": 130.0, "boy": 95.0,
    "tohum": 5,
    "kenar_bosluk": 2.0, "ic_payi": 1.0,
    "katman": 6, "duzlemler": {"In1.Cu": "GND", "In4.Cu": "+3V3"},   # 6 katman: iç 1 toprak, iç 4 +3V3, diğerleri sinyal
}
