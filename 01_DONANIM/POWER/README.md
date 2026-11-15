# Operfly Power (OPFPWR)

Batarya gerilimini omurga gerilimine (12 V) çeviren, giriş gerilimini ve akımını ölçen güç kartı.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_power.kicad_pro`. Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py POWER operfly_power`.
- Şematik tamam: **düğüm** (`dugum`), **giriş** (`giris`), **12 V çevirici** (`cevirici`), **servo rayı ve akım
  algılayıcı girişi** (`servo`). ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.
- **Çevirici ilk taslaktır.** Üreticinin örnek devresinden ölçeklendi; benzetim (LTspice), ısıl hesap ve bir güç
  elektroniği mühendisinin gözden geçirmesi olmadan üretime gönderilmemelidir.

## 12 V çevirici kararları (15 Kasım 2026)

Üreticinin "12 V çıkış, 4-80 V giriş" örnek devresi (5 A) temel alındı ve 12,5 A'e (150 W) ölçeklendi.

1. **Denetleyici LT8705A**, 202 kHz (zamanlama direnci 215 k, örnek devredeki gibi).
2. **Tam güç 10 V ve üzeri girişte.** Giriş akımı 18 A ile sınırlandı (akım direnci 2 mohm, ayar direnci 33,2 k);
   10 V altında çıkış gücü kendiliğinden azalır (6 V'ta yaklaşık 100 W). 2S-3S araçlar 150 W çekmez; sınır,
   bobini ve giriş MOSFET'lerini makul boyutta tutar.
3. **Bobin 10 µH** (aday Coilcraft XAL1510-103). 60 V girişte akım dalgalanması yaklaşık 4,8 A (tepeden tepeye).
4. **Bobin akım direnci 4 mohm.** Üretici formülüyle üst sınır 6,5 mohm; önerilen %30 payla 4 mohm seçildi.
5. **MOSFET'ler:** giriş tarafı 100 V (örnek devredeki FDMS86101, ikişer adet), çıkış tarafı 40 V düşük dirençli
   (aday BSC014N04LS). Denetleyici kapıları yaklaşık 6,35 V ile sürer; tüm MOSFET'ler bu gerilimde tam açılmalı.
6. **Çıkış 12,1 V** (102 k / 11,3 k, örnek devredeki gibi). Denetleyicinin kendi beslemesi çıkıştan alınır (ısınmayı azaltır).
7. **Açılış eşiği:** giriş 5,65 V'u geçince çalışır, 5,42 V'un altında kapanır. Giriş 5,8 V'a sarkarsa yük azaltılır.
8. **Hafif yükte süreksiz çalışma** seçildi: çevirici girişe geri akım basmaz (ideal diyotlar geri akımı kesmek
   zorunda kalmaz).
9. **Çıkış akımı ayrıca ölçülmüyor;** aşırı akım koruması bobin akım sınırı ve Hub'daki port sigortalarıyla sağlanır.
10. **12 V ana çıkış XT60 ile Hub'a gider.** Omurga fişi 150 W taşıyamaz (port başına 6 A); omurga fişi 2 A kendini
    onaran sigortayla beslenir ve düğüm devresi buradan çalışır.
11. Çıkış gerilimi düğüm işlemcisine ölçüm için gider (PA2).

Doğrulanacaklar: bobin doyma akımı (akım sınırı tepe değeri yaklaşık 29 A), kompanzasyon (örnek devre değerleri:
16,5 k + 10 nF, 220 pF), MOSFET ısıl hesabı, giriş ve çıkış kondansatörlerinin dalgalanma akımı, 40 V MOSFET seçimi.

## Giriş sayfası kararları (15 Kasım 2026)

1. **İdeal diyot denetleyicisi LTC4359** (önceki aday LM74700 yerine). 4-80 V çalışır ve ters bağlantıya -40 V'a kadar
   dayanır; 65 V sınırlı aday, 60 V tasarım sınırında geçici gerilimlere pay bırakmıyordu. Devre üreticinin örnek
   devresiyle aynıdır (70 V ve 24 V kırpma diyotları, 1 k, 47 nF).
2. **MOSFET henüz seçilmedi:** 100 V, lojik seviye (4,5 V kapı gerilimiyle tam açılan), en çok 4 mohm. Düşük giriş
   geriliminde denetleyicinin kapı gerilimi 4,5 V'a kadar düşebildiği için lojik seviye şarttır.
3. **Batarya konnektörü XT60** (giriş başına). Sürekli akımı 150 W bütçeyle 4S ve üzeri için yeterlidir; 2S-3S'te tam
   güç çekilecekse daha büyük konnektör gerekir.
4. **Giriş ölçümü INA228**, 0,5 mohm akım direnciyle; her batarya gerilimi ayrıca işlemciye bölücüyle gider.
5. İşlemci pinleri: PA0/PA1 batarya gerilimleri, PB10/PB11 ölçüm entegresi (I2C), PB3 ölçüm uyarısı.

## Düğüm devresi (tüm kartlarda ortak)

`10_ORTAK_ARACLAR/kicad/dugum.py` her karta aynı devreyi ekler:

- Bir Operfly Bus portu, ters bağlantı ve aşırı gerilim koruması
- 12 V -> 5 V (AP63205) -> 3,3 V (LP5907)
- Düğüm işlemcisi STM32G0B1CET6, 16 MHz kristal, durum LED'i, hata ayıklama noktaları
- İki CAN FD alıcı-verici (TJA1051-3), koruma diyotları
- Güvenli eleman SE050
- İsteğe bağlı PPS girişi ve Ethernet hatları

Karta özel işler için boş işlemci pinleri: PA0-PA8, PB0, PB1, PB3, PB4, PB6, PB7, PB10, PB11, PC6, PC7, PD2, PD3.

## Servo rayı kararları (15 Kasım 2026)

1. **İki bağımsız regülatör** (TPS54560B, 60 V, 5 A, 400 kHz), çıkışları ideal diyotla (LTC4359) birleşir. Biri
   arızalanırsa diğeri rayı taşır; işlemci her regülatörün çıkışını ayrı ölçer ve arızayı bildirir.
2. **Çıkış 6,0 V, toplam 5 A sürekli** (yedeklilik korunacaksa). Gerilim iki direnç değiştirilerek 5,0-8,4 V arasında
   ayarlanır (değerler şematikte yazılı). Giriş 7 V'un altındayken (boşalmış 2S) ray 6 V'u tutamaz.
3. **Regülatörler varsayılan açık.** İşlemci çalışmasa da servo rayı vardır; işlemci isterse her birini kapatabilir.
4. **Kompanzasyon** üreticinin yöntemiyle hesaplandı (16,5 k + 6,8 nF, 47 pF; çıkış kondansatörü 3 x 47 µF).
   Hata yükselticisi geçiş iletkenliği 350 µA/V varsayıldı; üretici belgesiyle doğrulanacak.
5. **Giriş sınırı:** regülatör 60 V'a kadar çalışır (mutlak sınır 65 V). 12S yüksek gerilimli batarya (52,2 V) içindedir;
   60 V tasarım sınırında pay azdır, girişteki kırpma diyotlarına güvenir.
6. **400 A temassız akım algılayıcı karta takılmaz;** ana batarya kablosuna takılan harici algılayıcı 3 uçlu
   konnektörle bağlanır (5 V, sinyal, GND). Algılayıcı seçilmedi.
7. Servo çıkışı XT30.

Doğrulanacaklar: bobin (10 µH, doyma akımı en az 8 A), diyot ısıl hesabı, kompanzasyon, 6 V'ta ideal diyot
denetleyicisinin kapı gerilimi.

## Sıradaki adımlar

1. Çeviricinin ve servo regülatörlerinin benzetimle doğrulanması (kompanzasyon, verim, ısıl).
2. Seçilmeyen parçalar: giriş MOSFET'i, 400 A algılayıcı.
3. Isıl hesap ve kart katman planı; ardından kart çizimi.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_power.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py POWER operfly_power`.

- **Kart:** 125 x 90 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 200 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,60/0,30 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 1512 yol parçası, 252 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- **UYARI — BU KART BU HÂLİYLE ÜRETİLİP GÜÇ VERİLMEZ.** Yüksek akım taşıyan ağlar (batarya girişleri BAT_A/BAT_B, VIN_OR, VIN_SW, VIN, çevirici düğümleri CV_SW1/CV_SW2, 12V_OUT, servo rayı SERVO_V/SRV_A/SRV_B) otomatik yol çizici tarafından 0,25-0,6 mm genişliğinde yolla çizildi. Bu ağlar 18 A'e kadar akım taşır; bu genişlikteki yol birkaç amperde aşırı ısınır ve yanabilir. Bu ağların tamamı geniş bakır alanlar (birden çok katmanda, dikiş geçişleriyle) olarak elle yeniden çizilmelidir.
- 150 W çeviricinin (dört anahtarlı) güç katı yerleşimi, sıcak döngüleri, akım ölçme dirençlerinin dört uçlu bağlantısı ve MOSFET'lerin soğutması tasarlanmadı; bu bölüm bir güç elektroniği tasarımcısınca baştan yerleştirilmelidir.
- İdeal diyot denetleyicileri ve akım ölçer (0,5 mohm) için ölçüm hatları güç yolundan ayrılmadı.
- 60 V'a kadar giriş için katmanlar arası ve yollar arası yalıtım aralıkları ayrıca gözetilmedi (genel açıklık 0,125 mm).
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
