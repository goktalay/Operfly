# Operfly Pilot T ana kartı (OPFKTL)

12 kanal kumanda eden ve telemetriyi küçük ekranda gösteren model. Bu kart Pilot 12 ana kartının devresini
(batarya, şarj, beslemeler, kumanda radyosu) ve telemetri ekranını taşır; işlemci ve güvenli eleman ortak giriş
kartındadır (`01_DONANIM/KUMANDA_GIRIS`). İki kart arasındaki bağlantı: `13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_pilott.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_T operfly_pilott`.
- Şematik tamam, 4 sayfa: kök, batarya/şarj/USB/güç/3,3 V (`guc`), radyo ve giriş kartı bağlantısı (`radyo`),
  ekran (`ekran`). ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.
- `guc` ve `radyo` sayfaları Pilot 12 ile ortak kaynaktan üretilir (`10_ORTAK_ARACLAR/kicad/kumanda_ana.py`);
  o sayfaların kararları ve doğrulama listesi `01_DONANIM/KUMANDA_12/README.md` dosyasındadır ve burada da geçerlidir.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Pilot T = Pilot 12 + ekran.** Güç ve radyo bölümü birebir aynıdır; tek kaynak dosyadan üretilir, bir karttaki
   düzeltme diğerine kendiliğinden geçer. Telemetri kumanda radyosunun aynı bağlantısından gelir; ek radyo yoktur.
2. **Ekran: EA DOGM128W-6** (128 × 64 nokta, görünen alan 51 × 31 mm, siyah-beyaz, yarı geçirgen LCD). Gerekçe:
   güneş altında arka ışıksız okunur (renkli küçük ekranlar güneşte okunmaz), 0,3 mA çeker (batarya süresini
   etkilemez), tek 3,3 V besleme ve SPI ile çalışır, karta doğrudan lehimlenir, tek adet satın alınabilir.
   Telemetri için yeterlidir: 8 satır × 21 karakter ya da büyük rakamlarla 4 satır.
3. **Arka ışık: kehribar (EA LED55X46-A).** 3,3 V'tan yalnızca dirençle çalışır (beyaz arka ışık yükselten sürücü
   isterdi), ömrü 100.000 saattir ve gece gözü kamaştırmaz. İşlemci PWM ile kısar; gündüz kapalı kalabilir.
   Toplam yaklaşık 45 mA.
4. **Ekranı giriş kartındaki işlemci sürer.** Giriş kartının "ekran / genişleme" konnektöründen bu karta 10 telli
   düz kablo gelir (JST-GH 10, iki uçta aynı sıra). Böylece giriş kartı üç kumandada da değişmeden kalır.
5. **Ekran bu kartın 3,3 V'undan beslenir;** kablodaki 3,3 V ucu kullanılmaz (iki besleme yolu birleştirilmez).
6. **Güvenli durum:** kablo takılı değilken ya da işlemci sıfırlanırken ekran sıfırlamada tutulur, arka ışık kapalıdır.
7. **Ekranın iç gerilim yükselticisi kullanılır** (üreticinin tek beslemeli devresi, 9 adet 1 µF kondansatör);
   ayrı bir 12 V kaynağı gerekmez.

## Sahibinin bilmesi gerekenler

- **Ekran küçük ve tek renklidir;** harita ya da video göstermez. Harita ve video Pilot Pro'nun işidir.
- **Ekran ana kartın üstündedir;** kasada ekran penceresi ana kartın yerini belirler. Kasa tasarımında ekranın
  ayrı küçük bir karta alınması gerekirse devre aynen taşınır.
- **Ekran karta elle lehimlenir** (LCD fırın lehimine dayanmaz; üretici 80 °C üstünü yasaklar). Dizgi sonrasında
  ayrı bir işçilik adımıdır.
- **Soğukta ekran yavaşlar:** çalışma aralığı −20…+70 °C. Daha soğukta görüntü geç değişir; kumanda çalışmaya
  devam eder (ekran kumanda yolunun parçası değildir).
- **Çalışma süresi Pilot 12 ile hemen hemen aynıdır;** arka ışık sürekli açıkken yaklaşık 45 mA ek tüketim olur.

## Doğrulanacaklar

- **Ayak izi** (KiCad kütüphanesindeki `Display:EA_DOGM128-6`) üreticinin ölçü çizimiyle ve arka ışıklı yükseklikle
  (5,8 mm) karşılaştırılacak; ekranın bakış yönü (alttan / üstten) kasaya göre seçilecek (yazılım ayarı).
- **Arka ışık akımı ve parlaklığı** numunede ölçülecek; 82 Ω dirençler ve anahtarlama transistörü buna göre
  kesinleşecek. Gece görüş gözlüğüyle kullanım istenirse arka ışık rengi ve en düşük parlaklık ayrıca denenecek.
- **Kontrast ayarı** sıcaklık aralığında numunede denenecek.
- **Askeri sıcaklık aralığı hedefi** (−40 °C) bu ekranla karşılanmaz; gerekirse ısıtıcılı ya da geniş aralıklı
  ekran ayrıca değerlendirilecek.
- **Kablo boyu ve SPI hızı:** 10 telli kablo kısa tutulacak (öneri 10 cm altı); 33 Ω seri dirençlerle denenecek.
- Güç ve radyo bölümünün doğrulama listesi: `01_DONANIM/KUMANDA_12/README.md`.
