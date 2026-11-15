# Operfly Base (OPFBAS)

RTK baz istasyonu: yerde sabit durur, kendi konumunu ölçer ve araçlardaki Nav kartlarının santimetre düzeyinde
konum bulması için düzeltme verisi üretir. Nav kartının yer sürümüdür.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_base.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py BASE operfly_base`.
- Şematik tamam, 4 sayfa: kök, düğüm (`dugum`), GNSS alıcısı (`gnss`), çevre (`cevre`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.
- Şematik Nav ile ortak kaynaktan üretilir (`10_ORTAK_ARACLAR/kicad/nav_ana.py`); alıcı, anten beslemesi, saniye
  darbesi, servis USB'si ve microSD kararları `01_DONANIM/NAV/README.md` dosyasındadır ve burada da geçerlidir.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Base = Nav + dış besleme girişi − pusula.** Alıcı aynıdır (Septentrio mosaic-X5): baz istasyonu ile araçtaki
   alıcının aynı olması düzeltme verisinin uyumunu garanti eder ve tek tip parça stoklanır. Devre tek kaynaktan
   üretilir; Nav'daki bir düzeltme Base'e kendiliğinden geçer.
2. **Düzeltme verisi omurgadan çıkar:** alıcının ikinci seri portu → düğüm işlemcisi → CAN FD → yer radyosu
   (Ground Radio) ya da Pilot Pro → radyo bağlantısı → araçtaki Nav. Ayrı bir düzeltme radyosu yoktur.
3. **Dış besleme girişi (XT30, 9-16 V):** Base direk üstünde tek başına dururken 3-4 hücreli bataryadan ya da 12 V
   adaptörden beslenir. Omurga 12 V'u ile diyotlarla birleşir: hangisi varsa o besler, biri diğerine akım vermez.
   Kendini onaran 2 A sigorta ve ters bağlantı koruması vardır; işlemci giriş gerilimini ölçer (batarya uyarısı).
4. **Pusula yok:** sabit duran istasyonda gereksizdir.
5. **microSD ve servis USB'si Nav'daki gibi kalır:** ham ölçüm kaydı (sonradan hassas konum hesabı) ve alıcının
   ayar arayüzü baz istasyonunda da işe yarar.
6. **Saniye darbesi (PPS) omurgaya verilebilir:** yer birimlerinin saat eşlemesi için (Nav'daki üç durumlu sürücü).

## Sahibinin bilmesi gerekenler

- **Güç tüketimi düşüktür** (yaklaşık 2-3 W): 3 hücreli 5 Ah batarya ile bir günden uzun çalışır.
- **Baz istasyonunun doğruluğu konumunun ne kadar iyi bilindiğine bağlıdır.** Ya bilinen bir noktaya kurulur ya
  da açıldıktan sonra konumunu uzun süre ortalar (yazılım işi). Araçların *birbirine göre* konumu her durumda
  santimetre düzeyindedir; *mutlak* konum bazın kendi konum hatası kadar kayar.
- **Anten ayrıdır** ve gökyüzünü açık görmelidir; jeodezik (çok frekanslı, yer düzlemli) anten önerilir. Kart antene
  3,3 V verir; yalnız 5 V ile çalışan antenler için araya besleme ekleyici gerekir.
- **Dış besleme en çok 16 V'tur** (4 hücreli batarya dahil). 24 V'luk araç beslemesine doğrudan bağlanmaz.
- **PC adaptörü omurgaya güç vermez;** Base bilgisayarla kullanılırken dış beslemeden beslenir.

## Doğrulanacaklar

- Nav kartının doğrulama listesi (`01_DONANIM/NAV/README.md`) aynen geçerlidir.
- **İkinci anten girişi ve çift antenli alıcı seçeneği** Base'te kullanılmaz; ortak kaynaktan geldiği için şematikte
  durur (ikinci SMA dizilmeyebilir; üretim listesinde kesinleşecek).
- **Dış besleme:** diyot düşümü ve sigortanın soğukta/sıcakta davranışı numunede ölçülecek; 9 V altında 5 V
  regülatörünün çalışma sınırı denenecek.
- **Düzeltme verisinin omurga üzerinden gecikmesi ve bant genişliği** (CAN FD) çok araçlı sürüde ölçülecek.
- **Anten seçimi** ve kablo kaybı; yıldırım/aşırı gerilim koruması (direk üstü kullanımda anten hattına koruyucu).

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_base.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py BASE operfly_base`.

- **Kart:** 105 x 75 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 115 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 996 yol parçası, 208 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Anten hatları 0,35 mm genişlikte çizildi; 50 ohm empedans üreticinin katman dizilimiyle hesaplanıp doğrulanmadı, hat uzunluğu, kıvrımlar ve geçiş sayısı gözetilmedi. Menzil doğrudan bu hatlara bağlıdır.
- Kenar montajlı SMA konnektörlerinin uçları kart kenarından 0,35 mm içeride başlar; anten hatlarının çevresinde toprak dikiş geçişleri yok.
- GNSS alıcı modülünün (mosaic, LGA-239) altındaki ve çevresindeki bölge üreticinin yerleşim kılavuzuna göre düzenlenmedi; modül altından sinyal yolu geçip geçmediğine bakılmalı.
- Dış besleme girişinin (XT30, 2 A) yol genişliği ayrıca hesaplanmadı.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
