# Operfly Ground Radio — yer radyosu (OPFGRD)

Yer tarafının radyo ve dağıtım noktası: araçlarla geniş bant (video + telemetri) ve kumanda bağlantısını kurar,
yer cihazlarını (Pilot Pro, bilgisayar, Base, Tracker) birbirine bağlar. Direğe takılabilir; kendi güç girişi vardır.

## Durum (15 Kasım 2026): şematik tamam, kart çizimi (PCB) başlamadı

- KiCad projesi: `kicad/operfly_groundradio.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py YER_RADYO operfly_groundradio`.
- **Çizilenler (ERC 0 hata, 0 uyarı), 5 sayfa:** kök, düğüm devresi + 1. omurga portu (`dugum`), geniş bant radyo
  + iki Ethernet portu + 3,3 V ve 5 V beslemeleri (`genisbant`), kumanda radyosu + beslemesi + antenleri (`kumanda`),
  dış besleme girişi + 2., 3. ve 4. omurga portları (`guc`).
- Kart çizimi (PCB) başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **İki radyo da doğrulanmış devreleriyle geldi.** Geniş bant radyo (Microhard pMDDL2450 OEM) Radio kartındaki,
   kumanda radyosu (RFDesign RFD900ux-SMT) RX kartındaki devrenin aynısıdır. Böylece araç ve yer tarafında aynı
   modüller, aynı beslemeler ve aynı yazılım sürücüleri kullanılır.
2. **Tek işlemci iki radyoyu yönetir** (ortak düğüm devresi). Kumanda radyosu RX kartıyla aynı uçlardadır (USART2,
   akış denetimli); geniş bant radyonun seri portu ikinci porta (USART1, akış denetimli) bağlandı.
3. **Dört omurga portu vardır; yer tarafında yıldızın merkezi bu karttır** (araçta Hub'ın yaptığı iş). Dört portun
   CAN hatları ortaktır, sonlandırma 60 ohm'dur. Gerekçe: Pilot Pro, bilgisayar, Base ve Tracker aynı anda
   bağlanabilmeli; yer tarafına ayrıca bir Hub taşımak gerekmemeli.
4. **Ethernet iki portta vardır, ayrı bir anahtar entegresi yoktur.** Radyo modülünün iki Ethernet portu var:
   LAN portu 1. omurga portuna, WAN portu 2. omurga portuna gider; WAN portu modülün yazılımında LAN'a köprülenir
   (üretici bunu "ek anahtar portu" olarak tanımlıyor). Böylece Pilot Pro ve bilgisayar aynı anda bağlanır.
   3. ve 4. portlarda Ethernet yoktur (Base ve Tracker yalnızca CAN ve 12 V kullanır). Hız 100 Mbit'tir; radyonun
   kendi hızı en çok 25 Mbit olduğu için yeterlidir.
5. **Dış besleme girişi 9–16 V (XT30):** 3–4 hücreli batarya ya da 12 V adaptör. Giriş 7 A sigortalıdır; ters
   bağlantıyı ve geri beslemeyi diyot keser, 18 V üstünü kırpma diyodu keser. Base'in girişiyle aynı gerilim
   aralığı seçildi: ikisi aynı bataryadan ya da adaptörden beslenebilir.
6. **Kart portlara 12 V verir.** Ortak bara (dış girişten) dört porta ayrı ayrı, kendini onaran 2 A sigortalardan
   dağıtılır: Base ve Tracker ayrı güç kablosu istemeden bu karttan beslenir. Pilot Pro ve PC adaptörü omurgadan
   güç almaz.
7. **Kartın kendi beslemesi baradan ayrı bir diyotla alınır;** dış giriş yokken portlardan birinden 12 V gelirse
   kart yine çalışır.
8. **İşlemci dış giriş gerilimini ölçer** (batarya ile çalışırken düşük gerilim uyarısı için).

## Sahibinin bilmesi gerekenler

- **Ethernet (video) iki cihaza kadar dağıtılır** (1. ve 2. port). Üçüncü bir Ethernet cihazı gerekirse araya
  Hub ya da hazır bir ağ anahtarı girer.
- **Besleme 9–16 V'tur; 24 V'a bağlanmaz.** Direk üstünde uzun kabloyla beslenecekse kablo kalınlığı gerilim
  düşümüne göre seçilmelidir (kart tek başına 12 V'ta yaklaşık 1–1,3 A çeker; Tracker eklenince artar).
- **Kart tam güçte yaklaşık 12–15 W ısı üretir** (geniş bant radyo yaklaşık 9 W). Direk üstünde, güneş altında
  kapalı kutuda soğutma kasa tasarımının ana konusudur; radyo modülüne soğutucu şarttır.
- **Dört anten vardır:** geniş bant radyo için iki (modülün üstündeki U.FL konnektörlerden kabloyla kasadaki
  SMA'lara), kumanda radyosu için iki (kart kenarında SMA). Yönlü antenle Tracker kullanılacaksa antenler ona göre
  seçilir.
- **Frekans ve güç izinleri** Radio ve RX kartlarıyla aynıdır: 2,4 GHz'te 1 W ve 902–928 MHz Türkiye/AB'de hukuki
  teyit ister (`01_DONANIM/RADIO/README.md`, `01_DONANIM/RX/README.md`). Yer istasyonunda yüksek kazançlı anten
  kullanmak yayılan gücü ayrıca artırır.
- **Düzeltme verisi (RTK):** Base'den CAN ile gelir, bu kart radyoyla araçlara yayar; ayrı bir düzeltme radyosu yoktur.

## Doğrulanacaklar

- **Modülün ikinci Ethernet portu (WAN):** LAN portuyla aynı çevre devresiyle çizildi (49,9 ohm, ferrit üzerinden
  ortak ETH_BIAS, aynı trafo). Üreticinin kılavuzundaki örnek devre (Ek C) ile ikinci port için de karşılaştırılacak;
  WAN portunun LAN'a köprülenmesi ve iki portun birlikte hızı numunede denenecek.
- **Dört portlu CAN yıldızı:** kablo boyları ve yansımalar numunede ölçülecek (uzun kablolarda hız düşürülebilir);
  PC adaptörünün kendi 120 ohm sonlandırmasıyla birlikte toplam yük denetlenecek.
- **Güç:** giriş diyodu (PDS760) tam yükte ısınır (5 A'da yaklaşık 2,5 W); bakır alanı buna göre verilecek. Port
  sigortalarının 2 A değeri Tracker'ın motor akımı belli olunca gözden geçirilecek.
- **Radyoların birbirini etkilemesi:** 900 MHz ve 2,4 GHz vericiler aynı kartta; anten yerleşimi ve süzme numunede
  ölçülecek.
- Geniş bant radyo bölümü Radio kartının, kumanda radyosu bölümü RX kartının doğrulama listesini devralır.
- **Üretim betiği:** radyo devreleri Radio ve RX betiklerinden kopyalandı (ağ adları farklı); ileride ortak modüle
  taşınabilir.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_groundradio.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py YER_RADYO operfly_groundradio`.

- **Kart:** 130 x 95 mm, 6 katman (iç 1: toprak, iç 4: +3V3; diğer katmanlar sinyal, elemanlar üstte), 173 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,60/0,30 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 1320 yol parçası, 264 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Anten hatları 0,35 mm genişlikte çizildi; 50 ohm empedans üreticinin katman dizilimiyle doğrulanmadı, hat uzunluğu ve geçiş sayısı gözetilmedi.
- Geniş bant modülü (pMDDL2450) tam güçte yaklaşık 7,5 W ısı üretir: ısıl geçişler, soğutucu ve montaj tasarlanmadı. Bu yapılmadan modül tam güçte çalıştırılmamalı.
- İki radyo modülü (2,4 GHz ve 900 MHz) birbirinden ve anahtarlamalı regülatörlerden uzak tutulmadı; karşılıklı girişim ölçülmeli.
- Dış besleme girişi (7 A sigortalı) ve dört port beslemesi (port başına 2 A) dar yolla çizildi; bu hatlar geniş bakırla yeniden çizilmeden kart tam yükte kullanılmaz.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
