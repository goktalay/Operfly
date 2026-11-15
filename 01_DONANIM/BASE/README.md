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
