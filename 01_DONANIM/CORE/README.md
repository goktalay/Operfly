
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
  (`sensorler`), IO işlemcisi ve çıkışlar (`io`), gözetim/enerji deposu/Peltier (`gozetim`).
- Durum: şematik tamam; ERC 0 hata, 0 uyarı. Sıradaki iş doğrulama listesi ve kart çizimi.
- Diğer kartlar ortak yardımcıları kullanır: `10_ORTAK_ARACLAR/kicad/kart.py` ve `dugum.py` (düğüm devresi).

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

### Doğrulanacaklar (kart çizimine geçmeden)

- BMP390 ve SE050 ayak izleri geçici; üretici çizimiyle yapılacak. IMU ayak izlerinde pin sırası bir kez daha bakılacak.
- IST8310 VPP ucu boş bırakıldı; üretici belgesindeki öneriyle karşılaştırılacak.
- ICM-42688-P ayrılmış uçları: 7 ve 11 GND'ye, 2, 3 ve 10 boş.
- TMUX1574: seçme girişinin yönü (0 = A kolu) ve 5 V beslemede 3,3 V lojikle sürülmesi.
- STM32G0B1 fabrika yükleyicisinin PA2/PA3 seri hattını desteklediği (boş işlemcinin ana işlemci üzerinden yüklenmesi).
- TPS3808G01 eşik gerilimi (0,405 V varsayıldı) ve 470 µF 25 V kondansatörün 8x10 mm kılıfta bulunabilirliği.
- Enerji deposunun ilk şarj akımı: Hub port anahtarı yaklaşık 1000 µF yükü açılışta kaldırmalı.

## Gözetim ve Peltier kararları (15 Kasım 2026; sahibi kararı tasarımcıya bıraktı)

1. **Harici watchdog ana işlemciyi sıfırlamaz, IO işlemcisini uyarır.** Ana işlemci darbe göndermeyi keserse
   `FMU_FAULT_N` 200 ms sıfıra iner; IO işlemcisi 1-8. çıkışları devralır ve güvenli değerleri sürer. Gerekçe: uçuşta
   donanımın kendiliğinden sıfırlama yapması, yazılım güncelleme ve hata ayıklama sırasında da tetiklenir ve sıfırlama
   döngüsüne yol açabilir. Ana işlemci takılırsa kendi iç watchdog'u onu sıfırlar; o yeniden başlayana kadar uçağı IO
   işlemcisi tutar.
2. **Watchdog penceresi:** darbe aralığı 10-93 ms arasında olmalı (yazılım 30-50 ms'de bir gönderir); kesinti en geç
   yaklaşık 125 ms içinde algılanır. Watchdog IO işlemcisinin beslemesinden çalışır.
3. **IO işlemcisi ana işlemciyi sıfırlayabilsin diye bir hat ayrıldı** (`IO_FMU_RST`) ama direnci dizilmez. İleride
   istenirse tek direnç takılarak açılır.
4. **Güç kesintisi algılama:** giriş 10,1 V altına inince `PWR_FAIL_N` sıfıra iner; işlemci kritik durumu FRAM'e yazar.
5. **Enerji deposu: 2 x 470 µF.** Kesintiden sonra kartı yaklaşık 10-20 ms taşır (kart tüketimi 2-3 W varsayımıyla
   hesap; ölçülecek). FRAM yazımı için yeterlidir; microSD'deki son birkaç yüz milisaniyelik kayıt kaybolabilir.
   Süper kondansatörlü daha uzun taşıma, kart alanı ve şarj devresi gerektirdiği için seçilmedi.
6. **Peltier sürücüsü: DRV8837**, 5 V'tan, en çok 1 A. Çıkışta bobin ve kondansatör var (anahtarlama gürültüsü pusula
   ve IMU'yu bozmasın diye). Isıl hedef varsayılan 45 °C, yazılımla değişir; sıcaklık IMU'ların kendi sensöründen okunur.
   Peltier modülünün kendisi mekanik tasarımla birlikte seçilecek (en çok 5 V, 1 A).

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_core.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py CORE operfly_core`.

- **Kart:** 115 x 80 mm, 6 katman (iç 1: toprak, iç 4: +3V3; diğer katmanlar sinyal, elemanlar üstte), 264 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,10 mm, açıklık 0,100 mm, geçiş 0,40/0,20 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim: KART TAMAMLANMADI.** DRC 0 ihlal (-), 10 bağlanmamış uç. Otomatik yol çizici bu kartı bitiremedi;
  kalan bağlantılar elle çizilmeli ya da yerleşim elle düzeltilip yeniden denenmeli.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- İşlemci 0,65 mm adımlı BGA olduğu için ince kural kullanıldı (yol ve açıklık 0,10 mm, geçiş 0,4/0,2 mm): bu, standart değil ileri sınıf üretim ister; üreticinin yetenekleriyle karşılaştırılmalı.
- Üç IMU'nun mekanik yalıtımı, ısıtıcı/Peltier bölgesi ve IMU'ların ısı kaynaklarından uzaklığı gözetilmedi; uçuş denetçisinde ölçüm kalitesi doğrudan buna bağlıdır.
- İşlemci çekirdek beslemesi ve BGA altı ayırma kondansatörleri üretici önerisine göre yerleştirilmedi; Ethernet (RMII), USB ve microSD hatları eşit uzunlukta çizilmedi.
- Servo/motor çıkışları (12 kanal) ve yedek işlemci yolu için gürültü ve arıza yalıtımı gözetilmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
