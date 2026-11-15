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
- Ekran seçimi (Pilot T): arayüzünün bu konnektöre uyduğu.
- SE050 ayak izi geçici (düğüm devresiyle ortak not).
