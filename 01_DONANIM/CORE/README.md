
## Pin haritası (15 Kasım 2026)

- Atamalar: `pin_atamalari.csv` (kaynak dosya). Okunabilir tablo: `PIN_HARITASI.md` (üretilir).
- Doğrulama: `python 10_ORTAK_ARACLAR/kicad/pin_cikar.py <KiCad>/symbols/MCU_ST_STM32H7.kicad_sym STM32H753IIKx out/h753iik.json`
  ardından `python 10_ORTAK_ARACLAR/kicad/pin_dogrula.py out/h753iik.json 01_DONANIM/CORE/pin_atamalari.csv 01_DONANIM/CORE/PIN_HARITASI.md "<başlık>"`.
- Kılıf: UFBGA 176+25, 10 x 10 mm, 0,65 mm adım.

Pin haritasından çıkan tasarım notları:

- İşlemcinin Ethernet arayüzü en çok 100 Mbit destekler (MII/RMII). Core–Hub bağlantısı 100 Mbit olur; PTP zaman damgası korunur.
  Core'daki PHY buna göre 10/100 RMII tipinde seçilecek. Omurganın geri kalanı gigabit kalır.
- Uçuş kaydı için microSD yuvası önerildi (SDMMC1 pinleri ayrıldı); onay bekliyor.
- Üç IMU ayrı SPI hatlarında ve ayrı besleme anahtarlarındadır; bir sensörün arızası diğerlerini etkilemez.
- 12 çıkış üç ayrı zamanlayıcıdadır (4 + 4 + 4); DShot ve PWM grupları buna göre seçilir.
