# Operfly kumanda giriş kartı

Üç kumandada (Pilot 12, Pilot T, Pilot Pro) ortak kart: çubukları, tekerlekleri, anahtarları ve düğmeleri okur.
Kumandanın gerçek zamanlı işlemcisi ve güvenli elemanı bu karttadır. Ana kartla bağlantı:
`13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_kumanda_giris.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_GIRIS operfly_kumanda_giris`.
- Şematik tamam, 3 sayfa: işlemci/güvenli eleman/bağlantılar (`islemci`), girişler (`girisler`).
  ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Kumandanın işlemcisi bu kartta.** Malzeme listesinde kumandalarda tek işlemci var ve giriş kartında sayılıyor;
   işlemci hem girişleri okur hem kumanda radyosunu sürer. Kumanda yolu Pilot Pro'daki Jetson'dan bağımsız kalır:
   Jetson kilitlense de araç kumanda edilebilir.
2. **Güvenli eleman (SE050) işlemcinin yanında**, ana kartta değil. Anahtarlar ve şifreleme aynı kartta kalır;
   kartlar arası kabloda anahtarla ilgili hat dolaşmaz.
3. **Omurga düğümü değil.** Kumandanın içinde CAN ve 12 V yok; ortak düğüm devresi yerine yalnızca işlemci, kristal
   ve güvenli eleman kullanıldı. İşlemci aynı (STM32G0B1CET6): yazılım araçları ve kimlik doğrulama kodu ortak.
4. **Ana kart bağlantısı 20 kontaklı yassı kablo:** besleme, kumanda radyosunun seri hatları ve denetimi, USB, I2C,
   güç düğmesi/tutma, sesli uyarıcı. Tanım ayrı belgede; Pilot 12, T ve Pro ana kartları buna uyacak.
5. **Çubuklar analog, oransal ölçüm.** Çubukların beslemesi ve işlemcinin ölçüm referansı aynı süzülmüş raydan
   (+3V3A) gelir; besleme dalgalanması ölçümü etkilemez. Her girişte 1 k + 100 nF.
6. **Anahtarlar tek analog girişle okunur.** İki 47 k orta konumu yarı gerilime çeker; aynı devre 2 ve 3 konumlu
   anahtarı okur, kopuk kablo "orta" göründüğü için arıza yazılımda anlaşılır. Altı anahtar altı giriş kullanır.
7. **12 kanal:** 4 çubuk ekseni + 2 tekerlek + 6 anahtar. Ayrıca 2 düğme ve menü için 5 yönlü tuş (tek analog giriş,
   direnç merdiveni).
8. **Çubuk ve anahtarlar kartta değil, kabloyla bağlanır** (kasaya vidalanan parçalar). Konnektör uç sıraları
   Operfly tanımıdır; satın alınan parçanın kablosu buna göre hazırlanır.
9. **Ekran/genişleme konnektörü** (SPI + denetim hatları): Pilot T'nin küçük ekranı için. Pilot 12'de boş kalır.
10. **USB işlemciden ana karta gider:** ayar, yazılım güncelleme ve (Pilot Pro'da) çubuk verisinin Jetson'a aktarımı.

## Sahibinin bilmesi gerekenler

- **Çubuk (gimbal) modeli seçilmedi.** Baktığım hazır Hall gimbal (RadioMaster AG01) 3,3 V ile çalışıyor; ancak
  ürün sayfalarında konnektör uç sırası ve çıkış gerilim aralığı yok. Kart bu yüzden kendi tanımladığımız
  4 uçlu girişle çizildi; seçilen gimbalin kablosu numune üzerinde ölçülerek uyarlanacak. Çıkışı analog olmayan
  (sayısal) bir gimbal seçilirse bu kart değişir.
- **Anahtar, tekerlek ve düğmeler de seçilmedi** (kasa tasarımıyla birlikte seçilecek).

## Doğrulanacaklar

- Seçilen gimbalin besleme akımı, çıkış aralığı (0-3,3 V içinde mi) ve uç sırası; gerekirse giriş bölücüsü.
- İşlemcinin 29 ve 32 numaralı uçları (BUZZER, LED_DURUM) USB-PD "ölü batarya" işleviyle paylaşımlıdır; açılışta
  bu uçlarda iç aşağı çekme bulunur, yazılım kapatmalıdır. Sesli uyarıcı ve ışık için sakıncası yok, denenecek.
- Analog girişlerin kaynak direnci (anahtarlarda yaklaşık 24 k) ile örnekleme süresi ayarı.
- Kullanıcının dokunduğu parçalardan (çubuk, anahtar gövdesi) gelebilecek statik boşalma: kasa topraklaması ve
  gerekirse giriş koruma diyotları kart çiziminde değerlendirilecek.
- Yassı kablonun kontak yönü ve uzunluğu (USB tam hız hattı taşıyor; kısa tutulacak).
- Ekran (Pilot T): EA DOGM128W-6 seçildi ve bu konnektöre uyuyor (bkz. `01_DONANIM/KUMANDA_T`); MISO ucu kullanılmıyor.
- SE050 ayak izi geçici (düğüm devresiyle ortak not).

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_kumanda_giris.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py KUMANDA_GIRIS operfly_kumanda_giris`.

- **Kart:** 75 x 55 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 102 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 768 yol parçası, 172 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- On beş konnektör kart kenarlarına otomatik dizildi; yerleri kumanda kasasındaki çubuk, anahtar ve düğmelerin konumuna göre seçilmedi (kasa henüz tasarlanmadı).
- Çubuk ölçüm hatları (analog) ve analog besleme (+3V3A) sayısal hatlardan ayrılmadı; çubuk okumalarındaki gürültü ölçülmeli.
- Yassı kablo konnektöründeki USB çifti eşit uzunlukta çizilmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
