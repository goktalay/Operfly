# Operfly Radio (OPFRAD)

Geniş bant bağlantı kartı: video ve telemetriyi taşır. Radyo modülünün Ethernet'i omurga ağına bağlanır; kartın düğüm
işlemcisi modülü yönetir (ayar, sıfırlama, durum) ve kartın kimliğini kanıtlar.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_radio.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py RADIO operfly_radio`.
- Şematik tamam, 3 sayfa: düğüm (`dugum`), radyo modülü/Ethernet/beslemeler (`radyo`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.
- Modülün sembolü ve ayak izi KiCad kütüphanesinde yok; ikisi de üreticinin işletme kılavuzundan
  (pMDDL Operating Manual v1.4.2) betikle üretildi (`kutuphane_uret.py`, `ayak_izi_uret.py`).

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Modül: Microhard pMDDL2450 OEM** (şartnamedeki seçim), karta lehimlenir (80 kenar pedi + alt toprak düzlemi).
2. **Ayrı Ethernet alıcı-vericisi yok.** Modülün içinde iki 10/100 portu var; yalnızca trafo gerekir. LAN portu trafo
   üzerinden omurganın A ve B çiftlerine bağlandı (Core ile aynı düzen, 100 Mbit). Devre üreticinin örneğidir.
   Malzeme listesindeki "gigabit Ethernet PHY" satırı Radio'dan çıkarıldı, trafo eklendi.
3. **İkinci Ethernet portu (WAN) ve USB kullanılmıyor**; uçları boş.
4. **Antenler kartta değil:** modülün üstündeki iki U.FL konnektörden kabloyla kasadaki SMA'lara gidilir. Kartta RF
   hattı olmadığı için kart çizimi kolaylaşır.
5. **3,3 V: AP63203 (12 V'tan, 2 A).** Modülün sayısal katı 0,5 A'ya kadar çeker; düğümün 250 mA'lık regülatörü
   yetmez, doğrusal regülatör de fazla ısınırdı. Düğüm işlemcisi aynı raydadır. Devre Core'dakinin aynısı.
6. **5 V verici beslemesi: ayrı AP63201 (sabit frekanslı).** Verici katı 30 dBm'de ortalama 1,2 A, anlık 1,5 A
   çeker; ayrı regülatör bu darbeleri düğümün 5 V rayından (CAN) uzak tutar. Sıfırlamada açıktır; işlemci
   gerektiğinde vericiyi susturabilir (radyo sessizliği, güç tasarrufu).
7. **İşlemci modülü yönetir:** seri port (akış denetimli), sıfırlama, CONFIG (fabrika ayarı ve kurtarma kipi),
   "modül çalışıyor" çıkışı, verici gerilimi ölçümü. Üretici RxD ve TxD'nin 0 ohm üzerinden dışarı alınmasını
   öneriyor (modül kurtarma); 0 ohm dirençler ve ölçüm noktaları kondu.
8. **Dört durum ışığı:** modül, alış, veriş, Ethernet. Çıkışlar açılışta belirsiz olduğu için aşağı çekildi.
9. **Soğutma:** modül yaklaşık 7,5 W ısı üretir. Üretici soğutucu ya da fan şart koşuyor; malzeme listesine
   soğutucu ve ısı dolgusu eklendi. Kasa tasarımında modülün kasaya ısı vermesi tercih edilecek.
10. **Ortak araçlar:** düğüm sayfasına "yalnızca A ve B Ethernet çiftleri" seçeneği eklendi.

## Sahibinin bilmesi gerekenler

- **Kart tam güçte verirken yaklaşık 9 W çeker** (12 V'ta 0,75 A) ve bunun çoğu ısıya döner. Küçük araçta soğutma ve batarya
  bütçesi buna göre düşünülmeli.
- **2,4 GHz'te 1 W çıkış hukuki teyit ister.** Modül ABD ve Kanada onaylıdır (kılavuz); Türkiye ve AB'de 2,4 GHz
  lisanssız kullanım sınırı bundan çok düşüktür. Frekans tahsisi ya da güç sınırlaması, açık duran hukuki
  teyit konusunun parçasıdır.
- **Bağlantı hızı 100 Mbit ile sınırlı değil, radyo ile sınırlıdır:** üretici 8 MHz kanalda en çok yaklaşık 25 Mbps
  veriyor; menzil arttıkça hız düşer.

## Doğrulanacaklar

- **Ayak izi:** ölçüler kılavuzdaki çizimlerden alındı (ped 1,83 x 0,81 mm, adım 1,27 mm, toprak düzlemi
  22,35 x 28,70 mm, lehim pastası deseni). Üretici köşelerde ±0,25 mm fazla malzeme olabileceğini söylüyor; kart
  çiziminden önce üreticinin güncel çizimiyle karşılaştırılacak.
- **Ethernet:** LAN portunun çapraz bağlantıyı kendiliğinden çözdüğü (Hub tarafı çözer, yine de denenecek);
  kullanılmayan WAN portu uçlarının boş bırakılabildiği.
- **USB_MODE ucu** boş bırakıldı (USB kullanılmıyor); üreticiye sorulacak.
- **Besleme toleransları:** kılavuz 3,3 V için 3,0-3,6 V veriyor; 5 V verici beslemesi için tolerans yazmıyor.
- **AP63201 çevre elemanları:** geri besleme üretici örnek devresinden (158 k / 30,1 k, 100 pF); bobin (10 µH)
  hesapla seçildi, üretici tablosu ve doyma akımıyla karşılaştırılacak (RX ile ortak). 2 A'lık regülatör 1,5 A
  anlık akımda sınıra yakın çalışır; ısı ölçülecek.
- **Soğutma tasarımı:** soğutucu yüksekliği, hava akışı ya da kasaya temas; sürekli tam güçte sıcaklık ölçümü.
- **Anten kabloları ve konnektör tipi** (U.FL-SMA; üretici kutulu sürümde ters kutuplu SMA kullanıyor).
- **Yazılım:** modülün ayar arayüzü (seri konsol), ağ ayarları, modül şifrelemesinin üzerinde Operfly şifrelemesi.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_radio.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py RADIO operfly_radio`.

- **Kart:** 110 x 75 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 112 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 799 yol parçası, 168 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Geniş bant modülü (pMDDL2450) tam güçte yaklaşık 7,5 W ısı üretir: modülün altındaki ısıl geçişler, soğutucu bağlantısı ve montaj delikleri tasarlanmadı. Bu yapılmadan modül tam güçte çalıştırılmamalı.
- Modülün 5 V verici beslemesi (darbeli, yüksek akım) ve Ethernet trafosu çevresi üretici yerleşim önerisine göre düzenlenmedi.
- Antenler modül üstündeki konnektörlerden kabloyla çıkar; kart üzerinde anten hattı yok.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
