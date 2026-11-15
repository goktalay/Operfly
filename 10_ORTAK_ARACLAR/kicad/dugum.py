"""Ortak düğüm devresi: Operfly Bus'a bağlanan her kartta aynı olan kısım.

İçerik: bir Operfly Bus portu, giriş koruması, 5 V ve 3,3 V besleme, düğüm işlemcisi (STM32G0B1CET6),
iki CAN FD alıcı-verici, güvenli eleman (SE050), durum LED'i, hata ayıklama noktaları, isteğe bağlı PPS girişi.

Dışarı verdiği ağlar: +12V (korumalı omurga gerilimi), +5V, +3V3, GND ve kartın `ek` ile istediği işlemci pinleri.
Düğüm işlemcisinin kart işlerine ayrılan boş pinleri: PA0-PA8, PB0, PB1, PB3, PB4, PB6, PB7, PB10, PB11, PC6, PC7, PD2, PD3.
"""
import os

from kart import C0603, C0805, C1206, XAL, Izgara
from sema_uret import Sema

# Düğümün kendi kullandığı pinler (KiCad pin verisindeki alternatif işlevlerle denetlendi).
DUGUM_PINLERI = {
    "PD0": "CAN_A_RX", "PD1": "CAN_A_TX", "PB12": "CAN_B_RX", "PB13": "CAN_B_TX",   # FDCAN1, FDCAN2
    "PB15": "CAN_A_S", "PB2": "CAN_B_S",
    "PB8": "SE_SCL", "PB9": "SE_SDA", "PB5": "SE_ENA",                               # I2C1
    "PA13": "SWDIO", "PA14": "SWCLK", "PF0": "HSE_IN", "PF1": "HSE_OUT", "PF2": "NRST",
    "PB14": "LED_DURUM",
}


def dugum_sayfasi(k, kok, dizin, x=25.4, y=50.8, ek=None, pps=False, ethernet=False, port=True, sonlandirma=False, besleme="omurga", ldo33=True):
    """k: Kart, kok: kök Sema. ek: {işlemci pini: ağ adı} karta özel bağlantılar. Sayfayı yazar ve döndürür.

    port=False: omurga portu bu sayfaya konmaz (Hub gibi portlarını kendi çizen kartlar); kart +12V_BUS ve CAN ağlarını
    kendi sağlar. sonlandirma=True: CAN sonlandırma dirençleri dizilir, toplam 60 ohm (yalnızca Hub);
    sonlandirma=120: 120 ohm dizilir (iki uçlu kısa bağlantının bir ucu olan kartlar, ör. PC adaptörü).
    besleme="harici": kart omurgadan beslenmez; +5V ve +3V3 ağlarını kart sağlar, port +12V uçları bağlanmaz.
    ethernet=True: omurga fişinin dört Ethernet çifti ETH_A+ ... ETH_D- ağlarına çıkar; ethernet=2: yalnızca A ve B.
    ldo33=False: 3,3 V regülatörü bu sayfaya konmaz; +3V3 ağını kart kendi (daha güçlü) regülatörüyle +5V'tan üretir.
    """
    harici = besleme == "harici"
    s = Sema(k.P, "Dugum devresi (omurga, besleme, islemci, CAN, guvenli eleman)", kagit="A1", tarih=k.T, ust=kok, ad="Dugum", genel_etiket=True)
    kok.alt_sayfa(s, "dugum.kicad_sch", x, y)
    ek = dict(ek or {})
    cakisan = set(ek) & set(DUGUM_PINLERI)
    assert not cakisan, "düğümün kendi pinleri karta verilemez: %s" % cakisan

    s.metin("OMURGA PORTU ve GIRIS KORUMASI: ters baglanti diyotu, 18 V kirpma diyotu. +12V korumali omurga gerilimidir.", 30, 30)
    baglanti = {"+12V": "+12V_BUS", "GND": "GND", "CAN_A_H": "CAN_A_H", "CAN_A_L": "CAN_A_L", "CAN_B_H": "CAN_B_H", "CAN_B_L": "CAN_B_L"}
    if pps:
        baglanti["PPS"] = "PPS_BUS"
    if ethernet:   # True: dort cift (gigabit); 2: yalnizca A ve B ciftleri (100 Mbit), C ve D bos kalir
        baglanti.update({"ETH_%s%s" % (c, i): "ETH_%s%s" % (c, i) for c in ("AB" if ethernet == 2 else "ABCD") for i in "+-"})
    if harici:
        del baglanti["+12V"]
    if port:
        k.koy(s, "operfly:Operfly_Bus_20", "J", "Operfly Bus", 70, 80, baglanti, "Connector_Harwin:Harwin_Gecko_G125-MS12005M2P_2x10_P1.25mm_Vertical")
    if not harici:
        g = Izgara(130, 70, sutun=12)
        k.iki(s, g, "Device:D_Schottky", "D", "B360A (60 V, 3 A)", "+12V", "+12V_BUS", "Diode_SMD:D_SMA")
        k.iki(s, g, "Device:D_TVS", "D", "SMBJ18A", "+12V", "GND", "Diode_SMD:D_SMB")
        k.C(s, g, "10u 50V", "+12V", fp=C1206); k.C(s, g, "100n 50V", "+12V", fp=C0603)
        for ag in ("+12V_BUS", "+12V", "GND"):
            k.bayrak(s, g, ag)

        if ldo33:
            s.metin("BESLEME: 12 V -> 5 V (AP63205, 2 A) -> 3,3 V (LP5907, 250 mA). 3,3 V'ta daha fazla akim isteyen kart kendi regulatorunu ekler.", 30, 125)
        else:
            s.metin("BESLEME: 12 V -> 5 V (AP63205, 2 A). 3,3 V bu kartta kendi sayfasindaki daha guclu regulatorle +5V'tan uretilir.", 30, 125)
        g = Izgara(50, 160, sutun=14)
        k.parca(s, g, "Regulator_Switching:AP63205WU", "U", "AP63205QWU",
                {"IN": "+12V", "EN": "EN_5V", "GND": "GND", "SW": "SW_5V", "BST": "BST_5V", "FB": "+5V"}, "Package_TO_SOT_SMD:TSOT-23-6")
        k.R(s, g, "100k", "+12V", "EN_5V"); k.C(s, g, "10u 50V", "+12V", fp=C1206); k.C(s, g, "100n", "BST_5V", "SW_5V")
        k.iki(s, g, "Device:L", "L", "4u7 XAL4020-472", "SW_5V", "+5V", XAL)
        k.C(s, g, "22u 16V", "+5V", fp=C1206); k.C(s, g, "22u 16V", "+5V", fp=C1206); k.bayrak(s, g, "+5V")
        if ldo33:
            k.parca(s, g, "Regulator_Linear:LP5907MFX-3.3", "U", "LP5907MFX-3.3", {"IN": "+5V", "EN": "+5V", "GND": "GND", "OUT": "+3V3"}, "Package_TO_SOT_SMD:SOT-23-5")
            k.C(s, g, "1u", "+5V"); k.C(s, g, "1u", "+3V3")

    else:
        g = Izgara(130, 70, sutun=12)
        k.bayrak(s, g, "GND")
    s.metin("DUGUM ISLEMCISI (STM32G0B1CET6): omurgaya iki CAN FD hattiyla baglanir, kimligini guvenli elemanla kanitlar.", 30, 215)
    ag = dict(DUGUM_PINLERI)
    if pps:
        ag["PA15"] = "PPS_IN"                                                       # TIM2_CH1
    ag.update(ek)
    ag.update({"VDD": "+3V3", "VBAT": "+3V3", "VREF+": "+3V3", "VSS": "GND"})
    lid = k.lib(s, "MCU_ST_STM32G0:STM32G0B1CETx")
    eksik = set(ag) - {ad for _no, ad, _x, _y, _a in s.pinler[lid]}
    assert not eksik, eksik
    k.koy(s, lid, "U", "STM32G0B1CET6", 110, 300, ag, "Package_QFP:LQFP-48_7x7mm_P0.5mm")
    g = Izgara(200, 250, sutun=12)
    for deger in ("4u7", "100n", "100n", "100n"):
        k.C(s, g, deger, "+3V3", fp=C0603 if deger == "4u7" else "Capacitor_SMD:C_0402_1005Metric")
    k.koy(s, "Device:Crystal_GND24", "Y", "16 MHz", *g.yer(), {"1": "HSE_IN", "3": "HSE_OUT", "2": "GND", "4": "GND"}, "Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm")
    k.C(s, g, "10p", "HSE_IN"); k.C(s, g, "10p", "HSE_OUT")
    k.R(s, g, "10k", "+3V3", "NRST"); k.C(s, g, "100n", "NRST")
    g.satir()
    k.iki(s, g, "Device:LED", "D", "LED yesil", "LED_DURUM", "LED_DURUM_A", "LED_SMD:LED_0603_1608Metric"); k.R(s, g, "1k", "+3V3", "LED_DURUM_A")
    for a in ("SWDIO", "SWCLK", "NRST"):
        k.olcum_noktasi(s, g, a)
    if pps:
        x0, y0 = g.yer(); g.yer()
        k.koy(s, "74xGxx:74LVC1G17", "U", "74LVC1G17", x0 + 15, y0, {"2": "PPS_BUF_IN", "4": "PPS_IN", "5": "+3V3", "3": "GND"}, "Package_TO_SOT_SMD:SOT-353_SC-70-5")
        k.R(s, g, "100R", "PPS_BUS", "PPS_BUF_IN"); k.R(s, g, "100k", "PPS_BUF_IN", "GND")

    s.metin("CAN FD: iki bagimsiz alici-verici (TJA1051-3). Sessiz mod girisi asagi cekili. Sonlandirma Hub'dadir; yerleri hazir, dizilmez.", 400, 30)
    g = Izgara(420, 70, sutun=12)
    for h in ("A", "B"):
        k.parca(s, g, "Interface_CAN_LIN:TJA1051TK-3", "U", "TJA1051TK/3", {
            "TXD": "CAN_%s_TX" % h, "RXD": "CAN_%s_RX" % h, "S": "CAN_%s_S" % h, "VCC": "+5V", "VIO": "+3V3", "GND": "GND",
            "CANH": "CAN_%s_H" % h, "CANL": "CAN_%s_L" % h}, "Package_SON:HVSON-8-1EP_3x3mm_P0.65mm_EP1.6x2.4mm", dx=15)
        k.C(s, g, "100n", "+5V"); k.C(s, g, "100n", "+3V3"); k.R(s, g, "10k", "CAN_%s_S" % h, "GND")
        k.koy(s, "Power_Protection:NUP2105L", "D", "NUP2105L", *g.yer(), {"1": "CAN_%s_H" % h, "2": "CAN_%s_L" % h, "3": "GND"}, "Package_TO_SOT_SMD:SOT-23")
        # Yıldız omurgada tek sonlandırma Hub'dadır: toplam 60 ohm (iki ucu sonlandırılmış hatla aynı yük).
        rt = "30R1" if sonlandirma is True else "60R4"
        k.R(s, g, rt, "CAN_%s_H" % h, "CAN_%s_TERM" % h, dnp=not sonlandirma); k.R(s, g, rt, "CAN_%s_L" % h, "CAN_%s_TERM" % h, dnp=not sonlandirma)
        k.C(s, g, "4n7", "CAN_%s_TERM" % h, dnp=not sonlandirma)
        g.satir()

    s.metin("GUVENLI ELEMAN (SE050): kart kimligi ve sertifikasi. SE_ENA sifira cekilince eleman kapanir (sifirlama).", 400, 150)
    g = Izgara(420, 195, sutun=12)
    x0, y0 = g.yer(); g.yer(); g.yer()
    k.koy(s, "operfly:SE050", "U", "SE050E2HQ1", x0 + 20, y0, {"I2C_SDA": "SE_SDA", "I2C_SCL": "SE_SCL", "ENA": "SE_ENA",
          "VIN": "+3V3", "VCC": "SE_VCC", "VOUT": "SE_VCC", "VSS": "GND", "EP": "GND"}, "Package_DFN_QFN:QFN-20-1EP_3x3mm_P0.4mm_EP1.65x1.65mm")
    k.R(s, g, "2k2", "+3V3", "SE_SCL"); k.R(s, g, "2k2", "+3V3", "SE_SDA"); k.R(s, g, "10k", "+3V3", "SE_ENA")
    k.C(s, g, "100n", "+3V3"); k.C(s, g, "2u2", "SE_VCC", fp=C0603)
    s.yaz(os.path.join(dizin, "dugum.kicad_sch"))
    return s
