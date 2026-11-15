# Operfly Range 10 / 30 / 100 (OPFR10, OPFR30, OPFR1H)

Mesafe sensörü kartı. Üç ürün aynı karttır: menzili karta takılan hazır lazer mesafe modülü belirler. Kart modülü
besler, okur ve mesafeyi omurgadan (CAN FD) yayınlar.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_range.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py RANGE operfly_range`.
- Şematik tamam, 3 sayfa: kök, düğüm (`dugum`), modül arayüzü (`sensor`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Sensör çekirdeği hazır modüldür;** kart yalnızca arayüzdür. Lazer mesafe ölçer tasarlamak (optik, göz
   güvenliği sertifikası) ayrı bir uzmanlık ve ürün işidir; hazır modül daha hızlı ve güvenli.
2. **Tek kart, üç ürün.** Aday modüllerin üçü de 5 V ile beslenir ve 3,3 V seviyeli seri portla konuşur; kart
   bunlara göre tasarlandı:
   - Range 10: Benewake TFmini Plus (12 m, 12 g)
   - Range 30: Benewake TF02-Pro (40 m, 50 g)
   - Range 100: Benewake TF03-100 (100 m, 77 g, IP67)
3. **Modül beslemesi anahtarlı ve sigortalı:** işlemci modülü kapatıp açabilir (takılırsa yeniden başlatma, güç
   tasarrufu); kablodaki kısa devre kartı ve omurgayı etkilemez.
4. **Seri port ve I2C birlikte çıkarıldı:** aynı konnektörle I2C ile çalışan başka modüller de bağlanabilir.
5. **Konnektör uç sırası Operfly tanımıdır** (JST-GH 6): modülün kendi kablosu bu sıraya göre hazırlanır.

## Sahibinin bilmesi gerekenler

- **Menziller hedefin yansıtıcılığına bağlıdır.** Üretici değerleri açık renkli (%90 yansıtan) hedef içindir;
  koyu zeminde düşer (ör. TF02-Pro %10 yansıtmada 13,5 m). Range 30 koyu zemin üzerinde 30 m göremeyebilir.
- **Modüller ayrı satın alınır** ve karta kabloyla bağlanır; kart ile modül aynı kasaya konur.
- **Başka üreticinin modülü de takılabilir** (5 V, 3,3 V seri port ya da I2C olması yeter); yazılımda o modülün
  protokolü gerekir.
- **TF03-100'ün CAN arayüzü kullanılmıyor;** modül seri porttan okunur, omurgaya kartın işlemcisi çıkar
  (güvenli eleman ve kart kimliği bu sayede korunur).

## Doğrulanacaklar

- **Modül seçimi numuneyle kesinleşecek:** gün ışığında, su ve çim üzerinde, titreşimde menzil ve kararlılık.
- **TF03-100'ün 5 V sürümü** sipariş edilmeli (6-24 V'luk RS-485/RS-232 sürümü bu karta uymaz).
- **Modüllerin kablo uç sıraları** üretici çiziminden alınıp Operfly konnektör sırasına göre kablo hazırlanacak.
- **Tepe akımı:** sigorta 0,5 A tutma akımlıdır; seçilen modülün açılış akımıyla denenecek.
- **Çalışma sıcaklığı:** aday modüllerin ikisi −20…+60 °C; askeri sıcaklık aralığı hedefi için değerlendirilecek.
- **Göz güvenliği sınıfı ve ihracat/ithalat koşulları** seçilen modül için teyit edilecek.
