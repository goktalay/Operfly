# Operfly Hub (OPFHUB)

Omurganın merkezi: 12 port, her portta elektronik sigorta ve akım ölçümü, CAN FD ve PPS dağıtımı, gigabit Ethernet anahtarı.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_hub.kicad_pro`. Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py HUB operfly_hub`.
- Şematik tamam, 8 sayfa: düğüm (`dugum`), güç girişi ve port denetimi (`guc`), 12 port ve sigortaları (`portlar`),
  anahtar beslemeleri (`anahtar_besleme`), üç Ethernet anahtarı sayfası (`anahtar_a/b/c`). ERC 0 hata, 0 uyarı.
- Kart çizimi başlamadı. Hub, ekosistemin en zor kartıdır (üç adet 128 uçlu entegre, 12 gigabit hat).

## Güç dağıtımı kararları (sahibi kararı tasarımcıya bıraktı)

1. **Port sigortası: TPS26630** (60 V, 6 A, iç direnci 31 mohm, akım ölçüm çıkışlı). Akım sınırı 6 A (3,01 k);
   omurga fişinin taşıyabildiği üst sınırla aynı. Daha düşük, karta özel sınırlar yazılımla uygulanır (işlemci port
   akımını ölçer ve portu kapatabilir).
2. **Aşırı akımda kendiliğinden yeniden dener** (kilitlenip kalmaz). Uçuşta geçici bir aşırı akım kartı kalıcı olarak
   kapatmasın diye seçildi; kalıcı arızada işlemci portu kapatır.
3. **Portlar varsayılan açık.** Kartlar kimlik doğrulaması için önce beslenmek zorunda; doğrulanmayan kartın yalnızca
   veri ağı kapatılır (Ethernet anahtarında), istenirse beslemesi de kesilir.
4. **Yumuşak açılış yaklaşık 11 ms** (47 nF): kartlardaki giriş kondansatörleri (Core'da yaklaşık 1000 µF) ani akım
   çekmeden dolar.
5. **Ortak eşikler:** giriş 9,6 V'u geçince portlar açılır, 9,0 V altında ve 15 V üstünde kapanır.
6. **Akım ölçümü:** her portun akım çıkışı (6 A = 3,0 V) 16 kanallı analog seçiciyle tek ADC girişine gelir.
7. **Port açma/kapama ve arıza okuma** iki adet 16 bitlik I2C genişleticiyle yapılır (PCA9555).
8. **CAN sonlandırması Hub'dadır:** hat başına toplam 60 ohm (2 x 30,1 ohm + 4,7 nF). Diğer kartlarda sonlandırma
   dizilmez.
9. **PPS** tüm portlarda ortak hattır; Nav sürer, diğer kartlar dinler.
10. **12 V girişi XT60** (Power kartından). Düğüm devresi 2 A sigortayla aynı hattan beslenir.

İşlemci pinleri: PA0 akım ölçümü, PA1 giriş gerilimi, PA4-PA7 seçici adresi, PB10/PB11 I2C, PB3 genişletici kesmesi.

## Ethernet anahtarı kararları (15 Kasım 2026)

1. **Üç adet KSZ9567R** (Microchip). Her biri 5 bakır gigabit port, 2 RGMII portu ve zaman eşleme (PTP) desteği taşır;
   belgeleri açıktır, pin tablosu doğrulanabildi. 12 bakır portlu tek entegre seçenekleri ayrıca araştırılmadı; kart
   alanını küçültmek istenirse sonraki revizyonda bakılabilir.
2. **Her anahtar dört omurga portuna hizmet eder** (A: 1-4, B: 5-8, C: 9-12); beşinci bakır portlar boş kalır (yedek).
3. **Anahtarlar RGMII ile zincirlenir:** A-B ve B-C. Uçtan uca en çok iki atlama. A ile C arasındaki trafik B'den
   geçer; B arızalanırsa A ve C birbirini göremez (kabul edilen risk; halka bağlantı sonraki revizyon seçeneği).
4. **Yönetim SPI ile düğüm işlemcisinden** (ortak hat, üç ayrı seçme ucu, ortak sıfırlama).
5. **Anahtarlar açılışta veri geçirmez** (başlatma ucu aşağı çekili). Düğüm işlemcisi kartların sertifikasını
   doğruladıktan sonra anahtarı başlatır ve portları tek tek açar. Kapalı ekosistem kuralının donanım karşılığıdır.
6. **Pin sırası üreticinin pin atama tablosundan alındı** ve ortak kütüphaneye işlendi (`KSZ9567R`, 128 uç + alt ped).
7. **Trafo: 4 çiftli gigabit modül** (TG111-MSC13LF), port başına bir adet. Entegre tarafındaki orta uçlar ayrı ayrı
   100 nF ile toprağa, kablo tarafı 75 ohm + 1 nF.
8. **Beslemeler:** 3,3 V, 2,5 V ve 1,2 V için üç aynı regülatör (TPS62130, 3 A). Analog beslemeler ferritle ayrılır.
9. **Port LED'i yok** (uçuş donanımı); durum yazılımdan okunur.

İşlemci pinleri (ek): PB3/PB4/PA2 SPI, PB6/PB7/PC6 seçme uçları, PC7 sıfırlama, PB0 genişletici kesmesi.

## Doğrulanacaklar

- TPS26630: akım sınırı formülü (18 / R kohm), kapatma girişinin (SHDN) 3,3 V lojikle sürülmesi, PGTH bölücüsü.
- 12 port aynı anda açılırken toplam ani akım (Power çeviricisinin akım sınırıyla birlikte).
- Yıldız topolojide CAN FD veri hızı üst sınırı (kablo boylarıyla ölçülecek).
- KSZ9567R: akım tüketimi (1,2 V ve 2,5 V hatları), kullanılmayan uçların (7. port, MII'ye özgü uçlar) bağlanma önerisi,
  RGMII saat gecikmesi ayarı (yazılımla), trafo orta uçlarının bağlanma biçimi, kristal yük kondansatörleri.
- KSZ9567R ayak izi geçici (alt pedli 128 uçlu kılıf çizilecek).
- TPS62130: sabit frekans ve çıkış ayar uçlarının bağlantısı, yumuşak başlatma kondansatörü.
- **Kart çizimi ön koşulu (15 Kasım 2026 taraması):** KSZ9567R'nin alt pedi (uç 129) seçili ayak izinde yok; KiCad
  kütüphanesinde alt pedli 128 uçlu TQFP ayak izi bulunmuyor. Kart çiziminden önce üretici kılıf çizimine göre ortak
  kütüphaneye alt pedli ayak izi eklenecek.
