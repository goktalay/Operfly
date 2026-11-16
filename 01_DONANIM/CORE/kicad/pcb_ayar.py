"""Operfly Core kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "en": 115.0, "boy": 80.0,
    "tohum": 1,
    "kenar_bosluk": 2.0, "ic_payi": 1.0,
    "sure_dk": 300,   # yol çiziciye tanınan süre (dakika)
    # İşlemci 0,65 mm adımlı BGA: toplar arasından çıkabilmek için ince kural (ileri üretim sınıfı).
    "sinif": (0.1, 0.1, 0.4, 0.2),
    "katman": 6, "duzlemler": {"In1.Cu": "GND", "In4.Cu": "+3V3"},   # 6 katman: iç 1 toprak, iç 4 +3V3, diğerleri sinyal
}
