# Operfly Power (OPFPWR)

Batarya gerilimini omurga gerilimine (12 V) çeviren, giriş gerilimini ve akımını ölçen güç kartı.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_power.kicad_pro`. Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py POWER operfly_power`.
- Çizilen: **düğüm devresi** (`dugum` sayfası). ERC 0 hata, 0 uyarı.
- Çizilmeyen: güç katı (aşağıda). Bu kısım üretici belgeleriyle hesap ister ve bir güç elektroniği mühendisinin
  gözden geçirmesi şarttır; betikle "kendiliğinden" üretilecek bir devre değildir.

## Düğüm devresi (tüm kartlarda ortak)

`10_ORTAK_ARACLAR/kicad/dugum.py` her karta aynı devreyi ekler:

- Bir Operfly Bus portu, ters bağlantı ve aşırı gerilim koruması
- 12 V -> 5 V (AP63205) -> 3,3 V (LP5907)
- Düğüm işlemcisi STM32G0B1CET6, 16 MHz kristal, durum LED'i, hata ayıklama noktaları
- İki CAN FD alıcı-verici (TJA1051-3), koruma diyotları
- Güvenli eleman SE050
- İsteğe bağlı PPS girişi ve Ethernet hatları

Karta özel işler için boş işlemci pinleri: PA0-PA8, PB0, PB1, PB3, PB4, PB6, PB7, PB10, PB11, PC6, PC7, PD2, PD3.

## Güç katı için alınan kararlar (çizim bekliyor)

Sahibi kararları tasarımcıya bıraktı; aşağıdakiler mimari karardır, parça değerleri hesaplanınca kesinleşir.

1. **Giriş aralığı 6-60 V** (2S-12S). 12 V'un altı ve üstü birlikte gerektiği için dört anahtarlı düşüren-yükselten
   çevirici kullanılır. Aday denetleyici: LT8705A (80 V sınıfı). 55 V sınırlı denetleyiciler 12S yüksek gerilimli
   bataryada pay bırakmadığı için elendi.
2. **Çıkış 12 V, 150 W** (12,5 A). Hub'ın 12 portu aynı anda tam yüklenmez; 150 W toplam bütçedir.
3. **Çift batarya girişi ideal diyotla birleşir** (aday: LM74700 + N kanal MOSFET, giriş başına). Diyot kaybı olmaz,
   bir batarya düşerse diğeri kesintisiz devralır.
4. **Giriş ölçümü:** gerilim, akım ve harcanan enerji için sayısal güç ölçer (aday: INA228, I2C ile düğüm işlemcisine).
5. **400 A temassız akım algılayıcı** ana batarya kablosu içindir (motor akımı karttan geçmez). Parça seçilmedi.
6. **Servo güç rayı:** yedekli, ayarlanabilir. Gerilim ve akım hedefi araç tipine bağlı; varsayılan öneri 6,0 V.

## Sıradaki adımlar

1. Güç katı hesabı: bobin, MOSFET'ler, akım algılama dirençleri, kompanzasyon (üretici tasarım aracıyla).
2. Şematik sayfaları: giriş ve ideal diyotlar, 12 V çevirici, ölçüm, servo rayı.
3. Isıl hesap ve kart katman planı; ardından kart çizimi.
