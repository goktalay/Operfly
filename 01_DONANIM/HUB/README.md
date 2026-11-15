# Operfly Hub (OPFHUB)

Omurganın merkezi: 12 port, her portta elektronik sigorta ve akım ölçümü, CAN FD ve PPS dağıtımı, gigabit Ethernet anahtarı.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_hub.kicad_pro`. Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py HUB operfly_hub`.
- Çizilen: düğüm devresi (`dugum`), güç girişi ve port denetimi (`guc`), 12 port ve sigortaları (`portlar`).
  ERC 0 hata, 0 uyarı.
- Çizilmeyen: **Ethernet anahtarı** ve port trafoları. Portların Ethernet uçları şimdilik bağlı değil.

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

## Ethernet anahtarı (çizim bekliyor)

- Gereksinim: 12 bakır gigabit port, zaman eşleme (PTP), port bazında açma/kapama, yönetim için düğüm işlemcisine bağlantı.
- KiCad standart kütüphanesinde 12 portluk bir anahtar entegresi yok; sembol üretici belgesindeki pin tablosundan
  çıkarılacak (100'ün üzerinde pin). Bu yüzden ayrı bir adım olarak ele alınıyor.
- Aday mimari: belgeleri açık, 5 bakır portlu ve PTP destekli anahtar entegrelerinden üç adet zincirlemek
  (aday aile: Microchip KSZ9477/KSZ9567). Seçim, belge doğrulamasından sonra kesinleşir.
- Her port için 4 çiftli gigabit trafo gerekir (12 adet).

## Doğrulanacaklar

- TPS26630: akım sınırı formülü (18 / R kohm), kapatma girişinin (SHDN) 3,3 V lojikle sürülmesi, PGTH bölücüsü.
- 12 port aynı anda açılırken toplam ani akım (Power çeviricisinin akım sınırıyla birlikte).
- Yıldız topolojide CAN FD veri hızı üst sınırı (kablo boylarıyla ölçülecek).
