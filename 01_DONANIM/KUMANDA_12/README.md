# Operfly Pilot 12 ana kartı (OPFK12)

Yalnızca 12 kanal kumanda eden, ekransız model. Bu kart bataryayı, şarjı, beslemeleri ve kumanda radyosunu taşır;
işlemci ve güvenli eleman ortak giriş kartındadır (`01_DONANIM/KUMANDA_GIRIS`). İki kart arasındaki bağlantı:
`13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_pilot12.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_12 operfly_pilot12`.
- Şematik tamam, 3 sayfa: batarya/şarj/USB/güç/3,3 V (`guc`), radyo ve giriş kartı bağlantısı (`radyo`).
  ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.
- Bu kartta işlemci yok; devre değerleri üretici veri sayfalarından alındı. Devrenin kaynağı Pilot T ile ortaktır:
  `10_ORTAK_ARACLAR/kicad/kumanda_ana.py` (veri sayfası listesi o dosyanın başında).

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Batarya tek hücre düzeninde (1S) Li-ion paket**, koruma devreli ve sıcaklık dirençli (10 k NTC). Tek hücrede
   şarj basit ve güvenlidir: hücre dengeleme gerekmez, USB'nin 5 V'u doğrudan yeter. İki hücreli düzen şarj için
   yükselten devre ve dengeleme isterdi.
2. **Şarj ve güç yolu: BQ24075.** USB takılıyken sistemi USB'den besler, kalan akımla bataryayı şarj eder; kumanda
   şarjdayken kullanılabilir ve şarjın bitişi sistem yükünden etkilenmez. Şarj akımı 1,0 A, güvenlik zamanlayıcısı
   yaklaşık 9 saat, batarya sıcaklığı 0-50 °C dışındaysa şarj durur.
3. **USB kaynağına göre şarj hızı.** Type-C kaynağı verebildiği akımı CC ucundaki gerilimle bildirir. Bir karşılaştırıcı
   (LMV393) bunu okur: standart USB portunda giriş akımı 0,5 A ile sınırlanır (porta zarar vermez), 1,5 A ya da 3 A
   verebilen kaynakta 1,36 A'ya çıkar. İşlemciye bağlı değildir.
4. **Güç açma/tutma şarj entegresinin SYSOFF girişiyle.** Kapalıyken batarya sistemden tamamen ayrılır. Düğmeye
   basınca sistem açılır, işlemci PWR_HOLD ile açık tutar, yazılım kapatınca yeniden ayrılır. USB takılınca
   kendiliğinden açılır; böylece şarj, işlemci yazılımı çalışmasa da başlar.
5. **Batarya ölçer: bq27441-G1A** (I2C). Kalan kapasiteyi yüzde olarak verir; düşük batarya uyarısı ALERT_N hattından.
   Batarya ile şarj entegresi arasında 10 mΩ ölçüm direnci var.
6. **3,3 V: TPS63001 (alçaltan-yükselten).** Batarya 3,0 V'a inse de, USB'de 5,5 V'a çıksa da 3,3 V sabit kalır.
   Sabit frekansta çalıştırıldı (çubuk ölçümleri için daha düşük gürültü).
7. **Radyo beslemesi: TPS61230 (yükselten), 5,2 V.** Modül verirken 1 A tepe akım çeker; entegre 3,3 V girişten
   2,1 A verebilir. USB'de giriş çıkıştan yüksek kalırsa entegre girişi doğrudan çıkışa aktarır (en çok 5,5 V;
   modülün sınırı içinde). Sıfırlamada açıktır, işlemci kesebilir.
8. **Radyo: RFD900ux-SMT**, RX kartındaki bağlantının aynısı (veri hatlarında 470 ohm, yazılım yükleme ucu işlemcide).
   İki SMA anten konnektörü.
9. **Sesli uyarıcı:** piezo, işlemcinin BUZZER çıkışından transistörle sürülür.
10. **USB veri hatları** koruma elemanından geçip yassı kabloyla giriş kartındaki işlemciye gider (ayar ve güncelleme).

## Sahibinin bilmesi gerekenler

- **Çalışma süresi (tahmin):** tam güçte (1 W) ortalama 2,5-3,5 W; 5000 mAh tek hücreyle (18 Wh) yaklaşık 5-7 saat.
  Verici gücü düşürülürse süre uzar. Gerçek değer ilk numunede ölçülecek.
- **Şarj süresi (tahmin):** 5000 mAh için 1,5 A verebilen kaynakta yaklaşık 6 saat; standart USB portunda (0,5 A)
  çok daha uzun. Daha hızlı şarj gerekirse anahtarlamalı şarj entegresine geçilir (sonraki revizyon).
- **Batarya paketi seçilmedi.** Kart tek hücreli, korumalı, NTC'li paket bekler (3 kontaklı JST-XH). NTC'siz paket
  kullanılırsa karttaki 10 k direnç dizilir ve sıcaklık koruması devre dışı kalır; önermem.
- **Frekans ve güç** konusu RX kartındakiyle aynıdır (aynı modül): hukuki teyit bekliyor.

## Doğrulanacaklar

- **Type-C eşiği:** 0,66 V eşik, standart (en çok 0,61 V) ile 1,5 A (en az 0,70 V) seviyelerinin arasında dar bir
  aralıktadır; referans bölücü %1 dirençlerle ve 3,3 V toleransıyla hesaplandı (0,62-0,69 V). Numunede farklı
  kaynaklarla denenecek; sorun çıkarsa %0,1 direnç ya da hazır Type-C denetleyici kullanılacak.
- **SYSOFF hattı:** entegrenin iç yukarı çekmesi yaklaşık 5 MΩ; düğme diyotu (BAT54C) üzerindeki gerilim düşük
  sıcaklıkta 0,4 V eşiğine yaklaşabilir. Soğukta açılma denenecek.
- **Ölü bataryayla USB'den açılış:** ilk anda giriş akımı 0,1 A ile sınırlıdır; 3,3 V gelince 0,5 A'ya çıkar. Radyo
  bu sırada açık olduğundan açılışın takılmadığı denenecek; gerekirse yazılım radyoyu batarya dolana kadar kapatır.
- **Standart USB portunda tam güçte verme:** 0,5 A giriş tek başına yetmez, fark bataryadan gelir (entegre bunu
  kendisi yapar); batarya boşken yazılım verici gücünü sınırlamalı.
- **TPS61230:** hafif yükte frekansı değişir (kapatılamaz); radyo alışına etkisi ölçülecek. Üretici örneğindeki
  XFL4020-102 yerine aynı değerde XAL4020-102 yazıldı (ayak izi uyumu doğrulanacak). Parçanın güncel üretim durumu
  ve muadili (TPS61230A girişi 4,5 V ile sınırlı olduğu için uymaz) kontrol edilecek.
- **bq27441-G1A:** batarya kapasitesi yazılımla girilmeli (varsayılan değerle yüzde yanlış çıkar).
- **Isı:** doğrusal şarjda entegre 1 A'da 1-2 W ısınır, kendini korumak için akımı düşürür; kart çiziminde alt pede
  bakır ve geçiş delikleri konacak. Radyo modülünün ısısı RX kartındaki notla aynıdır.
- **Anten konnektörü tipi ve yerleşimi** (kasa tasarımıyla).

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_pilot12.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py KUMANDA_12 operfly_pilot12`.

- **Kart:** 90 x 65 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 78 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 671 yol parçası, 110 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Anten hatları 0,35 mm genişlikte çizildi; 50 ohm empedans üreticinin katman dizilimiyle hesaplanıp doğrulanmadı, hat uzunluğu, kıvrımlar ve geçiş sayısı gözetilmedi. Menzil doğrudan bu hatlara bağlıdır.
- Kenar montajlı SMA konnektörlerinin uçları kart kenarından 0,35 mm içeride başlar; anten hatlarının çevresinde toprak dikiş geçişleri yok.
- Şarj devresi (BQ24075) ve alçaltan-yükselten regülatörün ısıl bakırı ve akım yolları ayrıca hesaplanmadı.
- Kart ölçüsü ve konnektör yerleri kumanda kasasına göre seçilmedi (kasa henüz tasarlanmadı); kasa belli olunca yerleşim yeniden yapılır.
- Batarya ölçerin akım direnci bağlantısı (dört uçlu ölçüm) gözetilmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
