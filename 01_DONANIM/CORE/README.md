
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

- Proje: `kicad/operfly_core.kicad_pro`. Şematik `kicad/uret.py` ile üretilir; `*.kicad_sch` dosyaları ve kütüphane
  tabloları elle düzenlenmez.
- Üretim ve denetim tek komut: `python 10_ORTAK_ARACLAR/kicad/denetle.py CORE operfly_core` (üretir, güncel biçime çevirir,
  ERC çalıştırır, `out/core.pdf` çıkarır).
- Sayfalar: kök (`operfly_core`), omurga portları (`omurga`), işlemci (`islemci`), güç (`guc`), saat/sıfırlama/ayırma
  kondansatörleri (`islemci_destek`).
- Durum: ERC 0 hata. Kalan uyarılar (tek uçlu etiketler) henüz çizilmemiş sayfalardan gelir: sensörler, IO işlemcisi ve
  çıkışlar, Ethernet/CAN, USB, microSD, gözetim ve Peltier sürücüsü.

## Güç ve işlemci destek kararları (15 Kasım 2026, sahibinin onayı beklenmeden alındı)

Bu kararlar gece çalışmasında, onay sorulmadan alındı. Her biri tek satırla geri alınabilir; değiştirilmesi istenen olursa
`kicad/uret.py` içinde ilgili satır düzeltilip şematik yeniden üretilir.

1. **İki omurga girişi diyotla birleştirilir** (2 x Schottky, 60 V 3 A). Basit ve arıza toleranslı; karşılığı diyot
   başına yaklaşık 0,4 V kayıp. İdeal diyot denetleyicisi (kayıpsız) sonraki revizyon için açık seçenek.
2. **Aşırı gerilim koruması:** girişte 18 V kırpma diyotu (SMBJ18A). Omurga 12 V olduğu için 18 V seçildi.
3. **5 V ve 3,3 V ayrı ayrı 12 V'tan üretilir** (AP63205 ve AP63203, 2 A, sabit çıkışlı). Biri arızalanırsa diğeri
   etkilenmez. Otomotiv sınıfı (Q) sürümleri -40..+125 °C çalışır; standart sürüm +85 °C ile sınırlıdır, bu yüzden
   malzeme listesine Q sürümü yazıldı.
4. **Her IMU'nun kendi 3,3 V regülatörü var** (LP5907, düşük gürültü), işlemci tek tek açıp kapatabilir (SENS1/2/3_EN).
   Varsayılan kapalıdır (aşağı çekme direnci); takılan bir sensör güç kesilerek sıfırlanabilir.
5. **Analog besleme** ferrit üzerinden süzülür; ADC referansı ayrıca 10 ohm + kondansatörle süzülür. Ayrı referans
   entegresi yok (ölçümler besleme izleme amaçlı, yüksek doğruluk gerekmiyor).
6. **Yedek pil yok:** VBAT 3,3 V'a bağlı. Saat bilgisi GNSS ve ağ zaman eşlemesinden gelir.
7. **Kristaller:** ana saat 16 MHz, gerçek zaman saati 32,768 kHz. Yük kondansatörü değerleri kristal parça numarası
   seçilince doğrulanacak.
8. **Açılış:** BOOT0 aşağı çekili (her zaman uygulamadan açılır). Fabrika yüklemesi SWD üzerinden yapılır.
9. **Besleme ölçümleri:** 12 V 11:1, 5 V ve 1. sensör beslemesi 2:1 bölücüyle işlemciye gider (36 V'a kadar güvenli).

Doğrulanacaklar (kart çizimine geçmeden): bobin parça numaraları ve doyma akımları, giriş diyotlarında ısıl hesap,
5 V hattının toplam akımı (IO işlemcisi, sensör regülatörleri, omurga dışı yükler), kristal yük kondansatörleri.
