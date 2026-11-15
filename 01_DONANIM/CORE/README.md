
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

## Mimari kararlar (15 Kasım 2026)

- **Çıkışlar:** 12 çıkışın ilk 8'i IO/failsafe işlemcisinin denetimindedir, son 4'ü doğrudan ana işlemciden çıkar.
  İlk 8 çıkışta ana işlemcinin zamanlayıcı sinyali ile IO işlemcisinin sinyali arasında seçim yapan bir anahtar bulunur;
  seçimi IO işlemcisi yapar. Ana işlemci çalışırken DShot dahil tüm protokoller ondan geçer; ana işlemci durursa
  IO işlemcisi çıkışları devralır ve güvenli değerleri sürer.
- **IO/failsafe işlemcisi omurgaya doğrudan bağlıdır (CAN B).** Kumanda alıcısı (RX) omurgada olduğu için IO işlemcisi,
  ana işlemci durduğunda kumandayı ancak CAN üzerinden alabilir. Bu yüzden CAN FD destekli bir işlemci gerekir;
  öneri düğüm işlemcisiyle aynı aile (STM32G0B1). Önceki STM32F103 önerisi CAN FD desteklemediği için bırakıldı.
- **İkinci Bus portu** yalnızca yedek güç ve CAN taşır; Ethernet ve PPS bağlı değildir.
- Sınır: DShot ile sürülen motorlarda IO işlemcisinin devralması motoru güvenli değere getiremez (ESC protokolü açılışta
  seçilir); bu çıkışlarda failsafe, sinyalin kesilmesiyle ESC'nin kendi davranışına dayanır. Servolar ve PWM ESC'lerde
  devralma tam çalışır.

## KiCad projesi (15 Kasım 2026)

- Proje: `kicad/operfly_core.kicad_pro`. Şematik `kicad/uret.py` ile üretilir; `*.kicad_sch` dosyaları elle düzenlenmez.
- Üretim: `python 01_DONANIM/CORE/kicad/uret.py`, ardından her sayfa için `kicad-cli sch upgrade` ve kök için `kicad-cli sch erc`.
- Sayfalar: kök (`operfly_core`), omurga portları (`omurga`), işlemci (`islemci`).
- Durum: iki Operfly Bus portu ve işlemci (97 sinyal + besleme pinleri etiketli) yerleşik. Güç katı, saat, sıfırlama,
  ayırma kondansatörleri, sensörler, IO işlemcisi ve çıkışlar henüz çizilmedi; ERC hataları bu eksiklerden gelir.
