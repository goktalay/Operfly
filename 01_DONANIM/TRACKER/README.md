# Operfly Tracker — anten takip birimi (OPFTRK)

Yer radyosunun (Ground Radio) yönlü antenini aracın konumuna göre iki eksende (yatay ve dikey) çevirir. 12 km
menzilde yer tarafındaki yönlü anten içindir. Ground Radio'nun omurga portlarından birine bağlanır.

## Durum (15 Kasım 2026): şematik tamam, kart çizimi (PCB) başlamadı

- KiCad projesi: `kicad/operfly_tracker.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py TRACKER operfly_tracker`.
- **Çizilenler (ERC 0 hata, 0 uyarı), 3 sayfa:** kök, düğüm devresi (`dugum`), iki adım motoru sürücüsü + referans
  anahtarı girişleri + açı algılayıcı konnektörleri (`motor`).
- **Motorlar ve mekanik (dişli, yatak, gövde) seçilmedi.** Kart bunları beklemez; aşağıdaki sınırlar içinde her
  iki fazlı adım motoruyla çalışır.
- Kart çizimi (PCB) başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **İki adım motoru (yatay ve dikey eksen).** Gerekçe: adım motoru dururken de tutar (rüzgârda anten kaymaz),
   konumu adım sayarak bilinir, ayrı bir konum algılayıcı şart değildir ve 12 V omurga gerilimiyle doğrudan çalışır.
   Hazır model servolarına göre hassasiyeti ve ömrü daha iyidir.
2. **Sürücü: eksen başına bir TMC2209.** Sessiz çalışır, akımı ve mikro adımı seri porttan ayarlanır, motorun
   zorlandığını (takılma, dayanma noktası) kendisi algılar. Çevre devresi üretilmiş açık kaynaklı bir sürücü
   kartındaki değerlerle aynıdır.
3. **Motor akımı faz başına yaklaşık 0,7 A'ya ayarlıdır** (donanım ayarı; yazılım düşürebilir, yükseltmek direnç
   değişikliği ister). Gerekçe: Tracker, Ground Radio'nun 2 A sigortalı portundan beslenir; iki motor birlikte bu
   sınırın içinde kalmalıdır.
4. **Sürücüler sıfırlamada kapalıdır;** işlemci açılıp kendini denetlemeden motorlara akım verilmez.
5. **Her eksende referans anahtarı girişi vardır.** Açılışta eksenler bilinen noktaya gider; sürücünün zorlanma
   algısı da aynı iş için kullanılabilir (anahtarsız), ama anahtar daha güvenilirdir.
6. **Her eksende isteğe bağlı açı algılayıcı konnektörü vardır** (mil ucundaki mıknatıslı algılayıcılar için, eksen
   başına ayrı I2C hattı). Adım kaçırmayı yakalar; rüzgârlı yerde ve ağır antende önerilir.
7. **Kartta pusula yoktur.** Motorların mıknatısları pusulayı bozar. Antenin baktığı yön kurulumda bir kez
   öğretilir (bilinen konumdaki araca ya da bir nişan noktasına çevrilerek); birimin kendi konumu Base'den ya da
   Pilot Pro'dan gelir.
8. **Aracın konumu omurgadan (CAN) gelir;** kartın radyoyla doğrudan bağlantısı yoktur.

## Sahibinin bilmesi gerekenler

- **Motor ve mekanik seçilmedi.** Öneri: iki fazlı, faz akımı 1 A'ya kadar, standart 42 mm gövdeli adım motorları
  ve antenin ağırlığına göre dişli ya da kayışlı aktarma. Antenin ağırlığı ve rüzgâr yükü belli olunca kesinleşir.
- **Yatay eksende kablo dolanması:** anten kabloları sınırsız dönüşe izin vermez. Dönüş yazılımla sınırlanır
  (örneğin ±200°) ya da döner bağlantı elemanı kullanılır; mekanik tasarım kararıdır.
- **Motor kablosu güç altındayken takılıp çıkarılmamalıdır;** sürücü zarar görebilir.
- **Güç:** iki motor dururken birlikte yaklaşık 5–8 W çeker (tahmin; motora göre değişir). Uzun süre beklemede
  yazılım tutma akımını düşürerek ısınmayı ve tüketimi azaltır.
- **Takip doğruluğu** aracın konum verisine, kurulumdaki yön hizalamasına ve mekanik boşluğa bağlıdır; dar hüzmeli
  antenlerde boşluksuz aktarma gerekir.

## Doğrulanacaklar

- **Sürücünün veri sayfası indirilemedi** (üretici sitesi buluttan erişilemiyor). Uç sırası KiCad kütüphanesinden,
  çevre değerleri üretilmiş açık kaynaklı bir sürücü kartının şematiğinden alındı; ikisi birbiriyle tutarlıdır.
  Kart çiziminden önce üretici veri sayfasıyla karşılaştırılacak: tek hatlı ayar portunun bağlantısı (işlemci TX
  ucunda 1 kΩ), adres seçimi (MS1, MS2), VREF–akım bağıntısı, taban pedinin ısıl tasarımı.
- **Akım algılama dirençleri** (0,11 Ω) 0805 kılıfta, 0,5 W sınıfı seçilmeli.
- **Motor geri beslemesi:** hızlı duruşta motor gerilim üretir; 12 V rayındaki kırpma diyodu ve kondansatörler
  (motor başına 100 µF) numunede ölçülecek.
- **Ground Radio port sigortası** (2 A) ile iki motorun kalkış akımı birlikte denenecek.
- **Referans anahtarı ve açı algılayıcı modelleri** seçilmedi; konnektör uç sıraları Operfly tanımıdır
  (referans: +3V3, sinyal, GND; açı algılayıcı: +3V3, GND, SCL, SDA).
- **Motor konnektörü uç sırası** Operfly tanımıdır (A1, A2, B1, B2); motor kablosu buna göre hazırlanır.
