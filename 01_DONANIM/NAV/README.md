# Operfly Nav (OPFNAV)

GNSS kartı: çok bantlı, çok takımyıldızlı RTK alıcısı; karıştırma ve aldatmayı tespit eder ve bastırır.
Konumu ve zamanı omurgaya verir; saniye darbesini (PPS) omurgaya süren karttır.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_nav.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py NAV operfly_nav`.
- Şematik tamam, 4 sayfa: düğüm (`dugum`), alıcı/besleme/antenler/saniye darbesi (`gnss`),
  servis USB'si/microSD/pusula/ışıklar (`cevre`). ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.
- Alıcının sembolü ve ayak izi KiCad kütüphanesinde yok; ikisi de üreticinin donanım kılavuzundan
  (mosaic Hardware Manual 1.11.0) betikle üretildi: `10_ORTAK_ARACLAR/kicad/mosaic_padleri.py` (239 padlik tablo,
  sayılarak denetlenir), `kutuphane_uret.py` (sembol), `ayak_izi_uret.py` (ayak izi).
- Şematiğin kaynağı Base kartıyla ortaktır: `10_ORTAK_ARACLAR/kicad/nav_ana.py` (Base = Nav + dış besleme − pusula).

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Alıcı Septentrio mosaic-X5** (şartnamedeki birinci seçenek). Aynı ayak izine çift antenli mosaic-H de oturur;
   kartta ikinci anten yolu hazırdır, mosaic-X5 dizgisinde dizilmez. Hangi modülün dizileceği siparişte seçilir.
2. **Ayrı RF ön ucu yok.** Alıcı, ana anten girişinde korumayı, anten beslemesini, 150 mA akım sınırını ve kısa devre
   kesmesini kendi içinde taşır; üretici anteni doğrudan bağlamayı önerir. Araya yükselteç koymak, etkin antenle birlikte
   kazancı alıcının kabul ettiği aralığın (15-50 dB) dışına taşıyabilirdi.
3. **Anten beslemesi 3,3 V, ayrı regülatörden (LP5907) ve işlemci denetiminde.** Sıfırlamada kapalıdır. Operfly Shield
   gibi kendi beslemesi olan bir kaynak bağlandığında anten ucuna doğru gerilim verilmez; kurulum sihirbazında anten
   tipi seçilince açılır. 3,3 V'tan yüksek besleme isteyen antenler bu revizyonda desteklenmez.
4. **3,3 V tek ray, AP7361C (1 A, doğrusal).** Alıcı tepe akımı için en az 0,5 A ister; düğümün 250 mA'lık regülatörü
   yetmez. Anahtarlamalı yerine doğrusal regülatör seçildi (RF yanında en düşük gürültü). İşlemci de aynı raydadır;
   böylece alıcı beslemesizken girişleri sürülemez (üretici uyarısı). Bedeli yaklaşık 0,6 W ısıdır.
5. **Saniye darbesi:** alıcı çıkışı 1,8 V'tur ve açılışta kısa süre belirsizdir. Seviye çevirici (SN74LVC1T45) 3,3 V'a
   çıkarır; üç durumlu tampon (74LVC1G125) omurgaya sürer. Tampon sıfırlamada kapalıdır, işlemci ancak zaman
   geçerliyken açar. Aynı omurgada iki Nav kartı olsa da hattı yalnızca seçilen kart sürer. İşlemci hem alıcının kendi
   darbesini hem omurgadaki darbeyi aynı sayaçla ölçer (TIM2, iki kanal).
6. **Alıcı ile işlemci arasında iki seri port:** COM1 (akış denetimli; ölçüm ve komut), COM2 (RTK düzeltmeleri).
   Düzeltmeler yer istasyonundan Operfly Radio ile gelir, omurgadan düğüm işlemcisine, oradan alıcıya aktarılır.
7. **Servis USB'si (Type-C) eklendi.** Alıcının ayar arayüzü ve yazılım güncellemesi USB üzerinden yapılır.
   Kartı beslemez; VBUS yalnızca alıcının USB katını besler. Devre üreticinin örneğidir.
8. **microSD eklendi** (ham ölçüm kaydı; haritalama uçuşlarında sonradan hassas konum hesabı için). Devre üreticinin
   örneğidir: 1 bit kip, DAT3 33 k ile yukarı çekili.
9. **Olay girişi:** işlemci alıcıya zaman işareti verebilir (örneğin kamera tetiği anı); alıcı anı 20 ns çözünürlükle
   kaydeder. 1,8 V giriş için 10 k / 12 k bölücü kullanıldı (alıcının iç aşağı çekme direnciyle hesaplandı).
10. **Pusula (IST8310) eklendi.** GNSS kartı güç kablolarından uzağa takıldığı için pusula burada Core'dakinden daha
    temiz ölçer. Core'daki pusula yedek kalır.
11. **Alıcının Ethernet arayüzü bu revizyonda kullanılmıyor** (harici alıcı-verici ister; malzeme listesinde yoktu).
    Tüm veri CAN FD üzerinden akar. Gerekirse sonraki revizyonda eklenir.
12. **Ortak araçlarda değişiklik:** düğüm sayfasına "3,3 V regülatörünü kart sağlar" seçeneği eklendi; üst üste duran
    uçlar (111 GND gibi) tek etiket alıyor. Diğer dört kartın ağ bağlantıları değişmedi (dördünde de ERC 0/0).

## Doğrulanacaklar

- **Ayak izi:** pad çapı 0,6 mm, adım 1,27 mm, lehim maskesi açıklığı pad + 75 µm üretici kılavuzundan alındı; kart
  çiziminden önce üreticinin güncel çizimi ve önerilen pad ölçüsüyle bir kez daha karşılaştırılacak.
- **Isı:** AP7361C SOT-223 kılıfı 0,6 W'ta ısınır (veri sayfası ısıl direnci 110 °C/W, geniş bakırla düşer). Kart
  çiziminde kılıf altına geniş bakır ve geçiş delikleri konacak; 85 °C ortamda yetmezse anahtarlamalı ön regülatöre
  geçilecek.
- **Besleme toleransı:** alıcı 3,3 V ±%5 ister (3,135-3,465 V); regülatör toleransı ve hat direnci birlikte hesaplanacak.
- **Operfly Shield çıkışı:** modülün RF çıkışında doğru gerilim olup olmadığı ve çıkış kazancı öğrenilecek; anten
  beslemesinin o durumda kapalı kalması buna göre kesinleşir.
- **Anten kazancı:** kullanılacak antenin kazancı eksi kablo kaybı 15-50 dB aralığında olmalı (mosaic-H ile 15-35 dB).
- **mosaic-H seçeneği:** bobin (Würth 744786139A) kılıfı ve koruma diyodu (SESD0402X1BN) ayak izi; iki antenin toplam
  akımı 150 mA'yı geçmemeli. RF hattındaki boş pedler kart çiziminde hattın üzerine konacak (saplama bırakılmayacak).
- **Kart çizimi kuralları (üretici):** anten hatları 50 ohm, toprak düzlemiyle çevrili; SD ve USB hatları iç katmanda;
  anten girişinin yakınından MHz düzeyinde sayısal hat geçmeyecek; alıcının yanına demir esaslı ekran kutusu konmayacak.
- **Pusula:** IST8310 VPP ucunun bağlantısı ve adres uçları (Core doğrulama listesiyle ortak); pusula, 5 V
  regülatörünün bobininden ve ferromanyetik parçalardan uzağa yerleştirilecek.
- **microSD koruma diyotları:** parça seçilmedi (0402, düşük sığalı).
- **USB:** ortak kip bobini konmadı (üretici "istenirse" diyor); EMC ölçümünde gerekirse eklenecek.
- **Yazılım:** alıcı sürücüsü, RTK düzeltme aktarımı, PPS ana kart seçimi ve karıştırma/aldatma bayraklarının
  omurgaya taşınması yazılacak.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_nav.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py NAV operfly_nav`.

- **Kart:** 100 x 75 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 114 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 1102 yol parçası, 232 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Anten hatları 0,35 mm genişlikte çizildi; 50 ohm empedans üreticinin katman dizilimiyle hesaplanıp doğrulanmadı, hat uzunluğu, kıvrımlar ve geçiş sayısı gözetilmedi. Menzil doğrudan bu hatlara bağlıdır.
- Kenar montajlı SMA konnektörlerinin uçları kart kenarından 0,35 mm içeride başlar; anten hatlarının çevresinde toprak dikiş geçişleri yok.
- GNSS alıcı modülünün (mosaic, LGA-239) altındaki ve çevresindeki bölge üreticinin yerleşim kılavuzuna göre düzenlenmedi; modül altından sinyal yolu geçip geçmediğine bakılmalı.
- Anten beslemesi (bias) süzgeci ve PPS hattı gürültü kaynaklarından ayrılmadı.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
