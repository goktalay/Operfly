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

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_tracker.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py TRACKER operfly_tracker`.

- **Kart:** 80 x 55 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 105 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 823 yol parçası, 165 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Motor sürücülerinin (2 × TMC2209) alt pedlerinden iç toprak düzlemine ısı geçişleri ve motor akımı (0,7 A) yollarının genişliği ayrıca hesaplanmadı.
- Akım ölçme dirençleri (BRA/BRB) sürücüye en kısa ve simetrik yoldan bağlanmadı.
- Motor konnektörleri sürücülerin yanına değil kart kenarına otomatik dizildi.
- Düzlemdeki bir kopukluk alt katmana dökülen küçük bir +3V3 yamasıyla giderildi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
