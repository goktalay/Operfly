# Operfly Vision (OPFVIS)

Görüntü işleme kartı: NVIDIA Jetson Orin NX (16 GB) taşıyıcısı. Orin Nano da aynı sokete takılır. Görevi kameradan
konum/hız desteği üretmek (GNSS'siz uçuş) ve hedef takibidir.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_vision.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py VISION operfly_vision`.
- Şematik tamam, 6 sayfa: kök, düğüm (`dugum`), güç (`guc`), Jetson soketi (`jetson`), Ethernet (`ethernet`),
  çevre birimleri (`cevre`). ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.
- Jetson soketinin 260 uçluk tablosu üreticinin veri sayfasından alındı (`10_ORTAK_ARACLAR/kicad/jetson_uclari.py`)
  ve açık kaynak bir Jetson Orin taşıyıcı kartındaki sembolle karşılaştırıldı (aynı).
- **Bu kart ekosistemin en zor ikinci kartıdır** (Hub'dan sonra): yüksek hızlı PCIe ve Ethernet hatları var.
  Kart çizimi mutlaka yüksek hızlı tasarım deneyimi olan biri tarafından yapılmalı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Jetson'a 12 V doğrudan verilir.** Orin NX/Nano 5-20 V kabul eder; ayrı 5 V çevirici gerekmez. Eski (yalnız 5 V)
   modüller MODULE_ID ucundan tanınır: işlemci önce bu ucu okur, eski modül takılıysa 12 V vermez.
2. **Jetson'ın açılıp kapanmasını düğüm işlemcisi yönetir:** beslemeyi verir (elektronik sigorta, 4 A), POWER_EN'i
   yükseltir, kapanma isteğini (SHUTDOWN_REQ) izler, sıfırlayabilir ve kurtarma kipine sokabilir. Böylece Jetson
   yer istasyonundan uzaktan kapatılıp açılabilir; takılırsa yeniden başlatılır.
3. **Omurga Ethernet'i Jetson'ın kendi gigabit portudur** (trafo üzerinden omurga fişine).
4. **İki kamera portunun her biri ayrı bir Ethernet denetleyicidir** (Intel I210, PCIe). Sıkıştırmasız kamera
   görüntüsü tek başına bir gigabit hattı doldurabilir; kameralar birbirinin ve omurganın hattını paylaşmaz.
   Her portta donanım zaman damgası (PTP) vardır: görüntü ile uçuş verisi aynı saate bağlanır.
5. **Kamera konnektörü Operfly Bus'tır:** 12 V (port başına 1,5 A sigortalı, işlemci açar), Ethernet ve tetikleme
   (PPS). Ekosistem içi kameralar tek kabloyla bağlanır.
6. **NVMe:** M.2 (Key M), dört şerit PCIe, kendi 3,3 V regülatörü (3 A).
7. **Karta özel IMU** (ICM-42688-P) Jetson'a bağlıdır: görüntü ve atalet ölçümü aynı işlemcide zamanlanır.
8. **Omurga PPS'i** hem Jetson'a hem iki Ethernet denetleyiciye gider (zaman eşleme); denetleyiciler kameraya
   tetikleme darbesi üretebilir.
9. **Taşıyıcı beslemeleri (3,3 V ve 1,8 V) yalnızca Jetson hazır olunca açılır** (üretici kuralı: modül kapalıyken
   uçlarına gerilim verilmez). Jetson'ın 1,8 V hatlarıyla işlemcinin 3,3 V hatları arasında seviye çevirici var.
10. **Giriş koruması** bu kartta P kanal MOSFET'tir (kart 3-4 A çeker; diğer kartlardaki 3 A'lık diyot yetmez).
11. **Kurtarma USB'si** (Type-C): Jetson'a ilk yazılım bu porttan yüklenir.
12. **Fan çıkışı** (5 V, 4 uçlu): hız Jetson'dan, devir bilgisi düğüm işlemcisine.

## Sahibinin bilmesi gerekenler

- **Güç:** Jetson tam yükte yaklaşık 25 W, iki kamera ve NVMe ile kart toplamı 40 W'a yaklaşabilir. Omurga portu
  70 W'a kadar verir; yeterli. Soğutma (soğutucu + fan) kasa tasarımının ana konusudur.
- **Ethernet denetleyicilerine fabrika ayarı yazılmalı.** I210 boş gelir; karttaki küçük belleğe üreticinin ayar
  dosyası (adres dahil) üretimde bir kez yazılır. Yazılmadan sürücü kartı tanımaz.
- **Kameralar seçilmedi.** Portlar gigabit Ethernet kameralar içindir (GigE). Kameranın 12 V'tan beslenmesi ve
  Operfly Bus konnektörü taşıması gerekir; hazır kameralar için ara kablo/adaptör kartı gerekebilir.
- **Jetson modülü ve NVMe ayrı satın alınır**, karta takılır.
- **Ters bağlantı ve aşırı akım koruması var; aşırı gerilimde (15,3 V üstü) Jetson ve kamera beslemeleri kapanır.**

## Doğrulanacaklar

- **Jetson soketi:** KiCad'in genel 260 uçlu soket ayak izi kullanıldı; Jetson için önerilen soket parça numarası,
  yüksekliği ve modül vida yerleri üreticinin tasarım kılavuzundan alınacak (kılavuz indirilemedi; veri sayfası
  kullanıldı).
- **Tasarım kılavuzu karşılaştırması:** POWER_EN gerilim seviyesi (işlemci 3,3 V sürüyor; uç 5 V'a dayanıklı analog
  giriş), SYS_RESET hattının regülatör açma uçlarını doğrudan sürmesi (1,8 V; regülatör eşiği 0,9 V), kullanılmayan
  PCIe saat isteği uçlarının toprağa bağlanması, USB algılama devresinin kutbu.
- **I210:** ayak izinin taban pedi ölçüsü; kullanılmayan NC-SI hakem girişi; LED kutbu; bellek tipi (üreticinin
  onaylı listesinden); kristal yük kondansatörleri kart sığasına göre.
- **Ethernet trafoları** Hub'daki tiptir (TG111-MSC13LF); I210 ve Jetson için üreticilerin önerdiği trafo
  listeleriyle karşılaştırılacak.
- **PCIe hatları:** kondansatör yerleri, çift uzunluk eşleme ve empedans kart çiziminde; M.2'de dördüncü nesil hız
  hedeflenmiyorsa üçüncü nesille sınırlandırılır.
- **Fan PWM seviyesi** ve Jetson kapalıyken fanın durduğu seçilen fanla denenecek. Bilinen risk: seviye çeviricinin
  çıkışında kendi 10 kΩ yukarı çekmesi vardır; karttaki 10 kΩ aşağı çekmeyle yüksek seviye 3,3 V'a çıkmaz (yaklaşık
  1,7 V). Fanın kendi yukarı çekmesi durumu değiştirir; gerekirse aşağı çekme 100 kΩ yapılacak.
- **Seviye çevirici** (TXS0104E) PPS kenar gecikmesi ölçülecek; gerekirse tek yönlü çeviriciye geçilir.
- **Kamera portlarında CAN yok;** kamera omurga düğümü olacaksa eklenir.
- **Isıl tasarım:** elektronik sigortalar, 3,3 V regülatörleri ve giriş MOSFET'i için bakır alanı.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_vision.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py VISION operfly_vision`.

- **Kart:** 150 x 105 mm, 6 katman (iç 1: toprak, iç 4: +3V3; diğer katmanlar sinyal, elemanlar üstte), 308 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,60/0,30 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 4399 yol parçası, 708 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- **Yüksek hızlı hatlar işlevsel sayılmaz:** PCIe (NVMe dört şerit ve iki Ethernet denetleyicisi), gigabit Ethernet ve USB çiftleri 85/90/100 ohm empedansta, eşit uzunlukta, kesintisiz toprak üstünde ve çift olarak çizilmedi; otomatik yol çizici bunları sıradan sinyal gibi çizdi. Bu hatlar NVIDIA tasarım kılavuzuna göre elle yeniden çizilmeden kart çalışmayabilir.
- Jetson soketinin ve M.2 yuvasının kart üzerindeki yeri, modüllerin yatacağı bölge, modül ve disk sabitleme delikleri ile soğutucu boşluğu tasarlanmadı; modüllerin altında kalan elemanların yüksekliği denetlenmedi.
- Jetson beslemesi (12 V, 4 A) ve 3,3 V regülatörlerin (5 A'e kadar) yolları dar çizildi; geniş bakırla yeniden çizilmeli.
- Kamera portlarının besleme (1,5 A) ve Ethernet trafosu çevresi üretici önerisine göre düzenlenmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
