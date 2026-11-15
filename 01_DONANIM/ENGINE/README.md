# Operfly Engine (OPFENG)

Benzinli motor kartı: devri, sıcaklıkları ve yakıtı ölçer, ateşleme beslemesini keserek motoru durdurabilir. Omurgaya
(CAN FD) diğer kartlar gibi bağlanır. Motor tarafındaki bütün bağlantılar omurgadan yalıtımlıdır.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_engine.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py ENGINE operfly_engine`.
- Şematik tamam, 4 sayfa: kök, düğüm (`dugum`), ölçüm adası (`olcum`), devir ve ateşleme (`atesleme`).
  ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Üç ayrı toprak.** Omurga (GND), ölçüm adası (GND_ISO) ve ateşleme beslemesi (IGN_GND). Aralarında yalnızca
   yalıtıcılar var. Ateşleme gürültüsü ve motor gövdesinden gelen toprak farkları omurgaya ve uçuş kartına geçmez.
2. **Ölçüm adası:** yalıtımlı besleme modülü (Murata NXE1S0505MC, 3 kV) + sayısal yalıtıcı (ISO7762) + 8 kanallı
   12 bit çevirici (MCP3208) + 4,096 V referans. İşlemci adayı SPI ile okur.
3. **İki termokupl girişi (K tipi, AD8495):** silindir kafası ve egzoz. Yaklaşık 800 °C'ye kadar. Gövdeye değen
   (topraklı) termokuplla da çalışır; kopuk termokupl algılanır.
4. **İki NTC girişi** (10 k): örneğin yağ/soğutma ve emme havası.
5. **Yakıt:** analog seviye girişi (0-5 V) ve akış ölçer darbe girişi. Sensör beslemesi (5 V) sigortalı.
6. **Devir girişi** optokuplörle yalıtımlı, iki uçlu: hem Hall sensörüyle hem ateşleme modülünün devir çıkışıyla
   kullanılabilir.
7. **Motor durdurma = ateşleme beslemesini kesmek.** Ateşleme bataryası karttan geçer (4,8-14 V, en çok 2 A).
   - **Anahtar kendiliğinden açıktır:** kart beslemesiz kalsa ya da arızalansa da motor çalışmaya devam eder.
     Uçuşta motorun yanlışlıkla durması, durdurulamamasından daha tehlikeli kabul edildi.
   - **Durdurmak için iki ayrı işlemci ucu birlikte gerekir;** tek bir uç arızası ya da açılış anındaki belirsiz durum
     motoru durdurmaz.
   - **Harici durdurma girişi:** iki ucu birleştiren bir anahtar motoru işlemciden bağımsız durdurur (yerde
     güvenlik için).
   - **Geri bildirim:** işlemci ateşleme çıkışında gerilim olup olmadığını ve ateşleme bataryasının gerilimini görür.

## Sahibinin bilmesi gerekenler

- **Kart arızasında motor durdurulamaz** (bilinçli tercih). Yerde güvenlik için ateşleme bataryası hattına ayrıca
  bir güvenlik fişi/anahtarı konmasını öneririm; karttaki harici durdurma girişi de bunun için var.
- **Ateşleme akımı sınırı 2 A.** Tek silindirli küçük motorların ateşleme modülleri için yeterli olmalı; seçilen
  motorun ateşleme akımı ölçülmeli. Çift ateşlemeli ya da büyük motorda anahtar büyütülür.
- **Egzoz sıcaklığı üst sınırı yaklaşık 800 °C.** Daha yükseği gerekirse referans ve kazanç değişir.
- **Sensörler seçilmedi:** termokupllar, NTC'ler, yakıt seviye ve akış sensörü, devir sensörü. Girişler yaygın
  tiplere göre tasarlandı; sensörler seçilince değerler gözden geçirilecek.
- **Ateşleme bataryası ters bağlanırsa kart korumaz** (anahtar ters yönde iletir). Konnektör yön kilitlidir.

## Doğrulanacaklar

- **Yalıtımlı besleme modülü düzenlemesizdir:** ada gerilimi yüke göre 4,5-5,5 V arasında değişir. 220 ohm ön yük
  en az yük şartını sağlar; yüksüz ve tam yükte gerilim numunede ölçülecek (çevirici ve yalıtıcı en çok 5,5 V ister).
- **AD8495 doğruluğu:** üretici ±2 °C'yi kart sıcaklığı 0-50 °C ve ölçüm −25…+400 °C için verir. Bunun dışında
  (egzoz, sıcak motor bölmesi) yazılımda doğrusallık düzeltmesi gerekir. Termokupl klemensi entegrenin hemen yanına
  konmalı (kart çizimi).
- **Termokupl klemensi** (vidalı, 2,54 mm) titreşim açısından kart çiziminde yeniden değerlendirilecek.
- **Devir girişi hızı:** optokuplör yavaştır; 2 kHz'e kadar darbe için uygundur (tek silindirde yeterli). Darbe
  genişliği çok dar olan ateşleme modüllerinde numunede denenecek.
- **Durdurma optokuplörü:** kapı direnci 22 k ile en kötü durumda (düşük sıcaklık, yaşlanma) transistörleri
  kapattığı doğrulanacak. Harici durdurma kablosu kapıya doğrudan gider; ateşleme gürültüsünde yanlış kesme
  olmadığı motor çalışırken denenecek (100 nF süzgeç var).
- **Anahtar ısısı:** iki DMP3099L paralel, 2 A'da toplam yaklaşık 0,2 W.
- **Yalıtım aralıkları** (üç toprak arası en az 3 mm önerilir) kart çiziminde uygulanacak; ekranlı kabloların
  ekranı yalnızca motor tarafında toprağa bağlanacak.
- **ISO7762 kullanılmayan kanal** girişi toprağa bağlı; yedek.
