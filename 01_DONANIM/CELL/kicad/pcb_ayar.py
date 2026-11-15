"""Operfly Cell kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "tohum": 2,
    "kenar_bosluk": 2.0, "ic_payi": 1.0,
    "katman": 6, "duzlemler": {"In1.Cu": "GND", "In4.Cu": "+3V3"},   # 6 katman: iç 1 toprak, iç 4 +3V3, diğerleri sinyal
    "en": 110.0, "boy": 85.0,
    # M.2 yuvası batı kenarına yakın, modem (30 x 52 mm) doğuya doğru kartın üstüne yatar; altı boş bırakılır.
    # Yuvanın yönü (çift numaralı uç sırası modemin girdiği yanda varsayıldı) üretici çizimiyle doğrulanacak.
    "sabit": {"J2": (10.0, 42.5, 90)},
    "yasak": [(16.0, 26.5, 68.0, 58.5)],
    "kenar": {"J1": ("G", 30.0), "J5": ("G", 80.0)},
}
