# Operfly Air (OPFAIR)

Hava hızı kartı: pitot tüpünden gelen fark basıncı, statik basıncı ve dış hava sıcaklığını ölçer, omurgadan (CAN FD)
yayınlar. Sabit kanatlı araçlarda zorunludur.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_air.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py AIR operfly_air`.
- Şematik tamam, 3 sayfa: kök, düğüm devresi (`dugum`), sensörler ve ısıtıcı (`sensor`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.
- Sensörün uç sırası KiCad kütüphanesinden alındı ve üretici veri sayfasıyla karşılaştırıldı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Fark basınç sensörü: TE MS5525DSO-DB001DS** (±1 psi = ±6,9 kPa, 24 bit, I2C, iki hortum uçlu). Ölçüm aralığı deniz
   seviyesinde yaklaşık 105 m/s'ye (yaklaşık 380 km/saat) kadar; ekosistemdeki hızlı araçları da kapsar. Zar tipi sensördür:
   hortumdan hava akmaz, hortum uzunluğu ve irtifa düzeltmesi gerekmez. Kendi sıcaklık ölçümü ve fabrika
   kalibrasyon katsayıları vardır.
2. **Statik basınç: BMP390** aynı I2C hattında (adresler 0x76 ve 0x77). Kart hava yoğunluğunu ve gerçek hava hızını
   kendi hesaplayabilir; Core'daki barometrelere yedek olur.
3. **Dış hava sıcaklığı:** gövde dışına konacak 10 k NTC için 2 uçlu giriş (JST-GH). Kart üstündeki sensörler kasa içi
   sıcaklığı gösterir; gerçek hava hızı için dış sıcaklık gerekir.
4. **Pitot ısıtıcı çıkışı:** 12 V, en çok 1 A (12 W). Buzlanma ve yoğuşmaya karşı. Korumalı anahtar (NCV8402: akım
   sınırı, aşırı sıcaklıkta kapanma), artı hatta kendini onaran sigorta. Sıfırlamada kapalıdır; yazılım açar ve
   darbe genişliğiyle gücü ayarlayabilir. İşlemci ısıtıcının takılı olup olmadığını ve arızayı ölçer (HEAT_SENS).
5. **Düğüm devresi** diğer kartlarla aynı (işlemci, iki CAN FD, güvenli eleman). Ethernet ve PPS kullanılmıyor.

## Sahibinin bilmesi gerekenler

- **Hortum bağlantısı:** sensörün Port 2 ucu pitot (toplam basınç), Port 1 ucu statik hatta bağlanır. Ters takılırsa
  hız eksi okunur; yazılım bunu yerde uyarı olarak gösterebilir.
- **Düşük hız doğruluğu sınırlı:** geniş aralık seçildiği için 10-15 m/s altında hata büyür (sıfır kayması birkaç
  on Pa olabilir). Her uçuştan önce yerde otomatik sıfırlama yapılır (yazılım). Yalnızca yavaş araçlar için daha
  dar aralıklı ikinci bir sürüm sonradan eklenebilir.
- **Pitot tüpü ve ısıtıcısı seçilmedi.** Isıtıcı 12 V ve en çok 1 A olmalı; daha güçlü ısıtıcı için anahtar ve
  konnektör büyütülür.
- **BMP390 kasa içi basıncı ölçer;** kasa hava alacak şekilde tasarlanmalı ya da statik hat kasaya bağlanmalı.

## Doğrulanacaklar

- **Sensör toplam hata bandı** veri sayfasında ±%2,5 tam ölçek; sıcaklıkla sıfır kayması numunede ölçülecek
  (ısıtıcı açıkken ve güneş altında).
- **BMP390 ayak izi** geçici (Core'daki notla aynı); üretici çizimiyle doğrulanacak.
- **NCV8402 ısısı:** 1 A'da 0,25-0,5 W; kart çiziminde drenaj pedine bakır alanı verilecek. Sürekli akım sınırı
  küçük pedde 1,5 A.
- **Isıtıcı algılama eşikleri** (HEAT_SENS) seçilen ısıtıcının direnciyle denenecek.
- **Isıtıcı darbe frekansı** basınç ölçümünü ve CAN hattını etkilemeyecek şekilde seçilecek (yazılım); gerekirse
  ısıtıcı hattına süzgeç eklenir.
- **Sigorta değeri** (1,5 A tutma) sıcak ortamda erken açmamalı; ısıtıcı seçilince yeniden bakılacak.
- **NTC tipi** (10 k, B = 3950 varsayıldı) ve dış sensörün yeri.

## Kart çizimi (15 Kasım 2026, otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_air.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py AIR operfly_air`.

- **Kart:** 60 x 45 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), elemanların
  tamamı üst yüzde, dört köşede M3 montaj deliği. Omurga portu batı kenarında, ısıtıcı ve dış sıcaklık
  konnektörleri doğu kenarında.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ve ısıtıcı ağları 0,40 mm, geçiş 0,8/0,4 mm;
  bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 551 yol parçası, 121 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- 5 V çeviricinin (U1, L1, giriş/çıkış kondansatörleri) anahtarlama döngüsü küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal (Y1) işlemciye en kısa yoldan bağlanmadı, altında başka sinyal geçip geçmediğine bakılmalı.
- CAN çiftleri (CAN_A, CAN_B) çift olarak ve eşit uzunlukta çizilmedi.
- Isıtıcı anahtarının (Q1) soğutma bakırı ayrıca hesaplanmadı; 1 A'da ısınması ölçülmeli.
- Basınç sensörünün (U7) hortum bağlantısı için mekanik boşluk ve sensörün ısı kaynaklarından uzaklığı gözetilmedi.
- Serigrafi yazıları (eleman adları) üretim katmanında bırakıldı; kart üstünde yazı yok.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
