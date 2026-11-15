
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
  kondansatörleri (`islemci_destek`), Ethernet/CAN/USB/microSD/PPS (`haberlesme`), sensörler/bellek/güvenli eleman
  (`sensorler`), IO işlemcisi ve çıkışlar (`io`).
- Durum: ERC 0 hata, 4 uyarı. Uyarılar henüz çizilmemiş iki devreden gelir: gözetim (harici watchdog ve enerji deposu:
  `WDG_KICK`, `PWR_FAIL_N`) ve Peltier sürücüsü (`PELTIER_PWM_A/B`). Bu ikisi sahibinin kararını bekliyor (aşağıda).

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

## Haberleşme kararları (15 Kasım 2026, sahibinin onayı beklenmeden alındı)

1. **Ethernet alıcı-vericisi LAN8742A**, 50 MHz osilatörle. Aynı saat hem alıcı-vericiye hem işlemciye gider; zaman
   eşlemesi (PTP) için en temiz düzen budur. Karşılığı: kristal yerine osilatör (biraz daha pahalı).
2. **Ethernet hattında trafo var** (Bourns PT61017PEL). Kartlar arası kabloda standart ve en güvenli yol; kartlar arasında
   toprak döngüsünü keser. Trafosuz (kondansatörlü) bağlantı yer kazandırır ama Hub tarafıyla birlikte kararlaştırılmalı.
3. **CAN alıcı-vericisi TJA1051-3** (CAN FD, 5 Mbit/s), her hatta ayrı. İşlemci pinindeki `CAN_x_STB` sinyali bu parçada
   "sessiz mod" girişidir (bekleme değil): yüksekken kart hattı yalnızca dinler.
4. **CAN sonlandırma dirençleri Core'da dizilmez**, yerleri hazırdır. Sonlandırma Hub'dadır.
5. **USB kartı beslemez.** Servis portu yalnızca veri taşır; kart her zaman omurgadan (12 V) beslenir. USB ile masa
   üstünde beslemek istenirse 5 V hattına güç seçici eklenmesi ve 3,3 V regülatörünün 5 V'tan beslenmesi gerekir
   (açık seçenek; ek parça ve kart alanı ister).
6. **microSD beslemesi anahtarlanmaz**, doğrudan 3,3 V'a bağlıdır. Kart kilitlenirse yeniden başlatma gerekir.
7. **PPS 3,3 V lojik** olarak tanımlandı ve omurga belgesine yazıldı. Core girişi 5 V'a dayanıklıdır.
8. `ETH_PPS_OUT` (işlemcinin ürettiği saniye darbesi) şimdilik yalnızca ölçüm noktasına çıkar.

Doğrulanacaklar: trafo pin sırası ve ayak izi (üretici belgesiyle), Hub tarafının 100 Mbit bağlantıda A/B çiftlerini
kullandığı, CAN hattında kabul edilen en yüksek hız için kablo boyu.

## Sensör ve IO işlemcisi kararları (15 Kasım 2026, sahibinin onayı beklenmeden alındı)

1. **Sensör beslemeleri:** 1. hat IMU 1 + barometre 1 + pusula, 2. hat IMU 2 + barometre 2, 3. hat IMU 3. Bir hat
   kapatıldığında o hattaki sensörlerin bağlı olduğu I2C hattı da kullanılamaz (yalnızca sıfırlama sırasında kapatılır).
2. **Barometre 2: MS5611-01BA03** (ICP-20100 yerine). Dağıtıcı ICP-20100'ü "yeni tasarımlar için önerilmez" olarak
   listeliyor. MS5611 farklı üretici ve farklı ölçüm ilkesi; barometre 1 (BMP390) ile ortak hata riskini azaltır.
3. **Güvenli eleman SE050:** `SE_NRST` hattı elemanın güç anahtarı girişini (ENA) sürer. I2C kullanımında ayrı bir
   sıfırlama girişi olmadığı için sıfırlama, beslemesini kesip vererek yapılır.
4. **FRAM: FM25V10** (1 Mbit, SOIC-8).
5. **IO/failsafe işlemcisi: STM32G0B1CET6** (LQFP-48). Kendi 3,3 V regülatörü, kendi kristali ve CAN B üzerinde kendi
   alıcı-vericisi vardır. Pin atamaları `io_pin_atamalari.csv` içindedir ve KiCad pin verisiyle denetlenmiştir.
6. **Çıkış seçici: 2 x TMUX1574** (analog anahtar). Sayısal seçici yerine analog anahtar seçildi çünkü iki yönlü motor
   protokollerini (telemetrili DShot) geçirir. Seçme girişi aşağı çekilidir: IO işlemcisi çalışmıyorken 1-8. çıkışları ana
   işlemci sürer; IO işlemcisi devralmak istediğinde girişi yükseltir. Anahtarlar 5 V'tan beslenir (iki 3,3 V hattından
   bağımsız).
7. **Çıkış konnektörü (26 kontak):** tek numaralı kontaklar 1-12. çıkış, çift numaralı kontaklar GND, 25. kontak boş.
   Her çıkışta 33 ohm seri direnç var. Çıkışlarda ayrıca ESD koruması yok (sonraki revizyon için açık).
8. **IO işlemcisi yazılım yükleme:** ana işlemci `IO_NRST` ile sıfırlar ve seri hattan yükler. `IO_BOOT0`, IO işlemcisinin
   BOOT0/SWCLK ortak pinine 10 k ile bağlıdır; hata ayıklayıcı takılıyken hata ayıklayıcı baskın gelir.
9. **Durum LED'leri** sıfırda yanar. Kart sürümü dirençleri A revizyonu için yerleştirildi (sürüm 1:1, revizyon 10:1).
10. **Hata ayıklama:** ana işlemci için 2x5 (1,27 mm) SWD konnektörü; konsol ve IO işlemcisi SWD hatları ölçüm noktasında.

### Sahibinin kararını bekleyenler (çizilmedi)

- **Harici watchdog ve enerji deposu** (`WDG_KICK`, `PWR_FAIL_N`): watchdog süresi dolduğunda ne olacağı bir güvenlik
  kararıdır (ana işlemci uçuşta sıfırlansın mı, yoksa yalnızca IO işlemcisi mi devralsın) ve enerji deposunun kaç
  milisaniye taşıyacağı belirlenmeli.
- **Peltier sürücüsü** (`PELTIER_PWM_A/B`): modül akımı ve IMU ısıl hedefi belli olmadan sürücü seçilemez.

### Doğrulanacaklar (kart çizimine geçmeden)

- BMP390 ve SE050 ayak izleri geçici; üretici çizimiyle yapılacak. IMU ayak izlerinde pin sırası bir kez daha bakılacak.
- IST8310 VPP ucu boş bırakıldı; üretici belgesindeki öneriyle karşılaştırılacak.
- ICM-42688-P ayrılmış uçları: 7 ve 11 GND'ye, 2, 3 ve 10 boş.
- TMUX1574: seçme girişinin yönü (0 = A kolu) ve 5 V beslemede 3,3 V lojikle sürülmesi.
- STM32G0B1 fabrika yükleyicisinin PA2/PA3 seri hattını desteklediği (boş işlemcinin ana işlemci üzerinden yüklenmesi).
