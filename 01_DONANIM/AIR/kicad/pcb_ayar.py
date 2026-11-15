"""Operfly Air kart çizimi ayarları (10_ORTAK_ARACLAR/kicad/pcb_yerlesim.py okur)."""
AYAR = {
    "en": 60.0, "boy": 45.0,
    "tohum": 2,   # bu tohumla DRC temiz çıktı (0 ihlal, 0 bağlanmamış uç)
    # Omurga portu batı kenarında; ısıtıcı ve dış sıcaklık konnektörleri doğu kenarında.
    "kenar": {"J1": ("B", 22.5), "J3": ("D", 16.0), "J2": ("D", 31.0)},
    # Isıtıcı akımını (1 A) taşıyan, adı "+" ile başlamayan ağlar da geniş yolla çizilir.
    "guc_aglari": ["HEAT_RET", "HEAT_DRV"],
}
