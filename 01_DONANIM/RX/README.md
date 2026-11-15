# Operfly RX (OPFRCV)

Araç tarafı kumanda alıcısı: kumandadan gelen 12 kanalı ve yedek telemetriyi taşır, kanalları omurgadan (CAN FD)
Core'a verir. Bağlantı kaybını Core'a bildirir.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_rx.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py RX operfly_rx`.
- Şematik tamam, 3 sayfa: düğüm (`dugum`), radyo modülü/besleme/antenler (`radyo`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.
- Modülün sembolü ve ayak izi KiCad kütüphanesinde yok; ikisi de üreticinin veri sayfasından
  (RFD900ux/RFD868ux Data Sheet V1.3) betikle üretildi (`kutuphane_uret.py`, `ayak_izi_uret.py`).

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Modül: RFDesign RFD900ux-SMT** (şartnamedeki "RFD900x sınıfı"nın karta lehimlenen sürümü, 21 x 29 mm).
   Üretici RFD900x ile uyumlu olduğunu belirtiyor. Kablolu sürüm yerine bu seçildi: tek kart, konnektör ve kablo yok,
   titreşime dayanıklı; anten konnektörleri kendi kartımızda. Kumandalar ve Ground Radio da aynı modülü kullanacak.
2. **868 MHz seçeneği aynı kartta:** RFD868ux-SMT aynı ayak izine oturur. Frekans kararı (aşağıda) kartı değiştirmez.
3. **Modüle ayrı besleme: AP63201, 12 V → 5,3 V.** Modül 5,0-5,5 V ister ve verirken 1 A tepe akım çeker.
   Düğümün 5 V rayı alt sınırda kalırdı; 5,3 V hedefi toleranslarla 5,15-5,43 V aralığında tutar. Sabit frekanslı
   (AP63201) sürüm seçildi; hafif yükte frekansı değişen sürüm radyoda istenmeyen bileşen üretebilir.
4. **Radyo beslemesi sıfırlamada açıktır.** İşlemci yeniden başlasa da radyo bağlantısı kopmaz (uçuş bağlantısı).
   İşlemci gerektiğinde besleme kesip açabilir; modülde sıfırlama ucu olmadığı için takılan modülü kurtarmanın yolu budur.
5. **Yazılım yükleme kipi:** modülün SWO ucu besleme açılırken sıfırda tutulursa modül yükleme kipine girer. Bu uç
   işlemciye bağlandı; modül yazılımı omurga üzerinden güncellenebilir, kartı sökmek gerekmez.
6. **Seri arayüz akış denetimli** (RTS/CTS), 3,3 V. İşlemciden modüle giden hatlarda 470 ohm var: modül beslemesi
   kapalıyken girişlerinden akım akmasını sınırlar.
7. **İki anten girişi doğrudan SMA'ya** (üretici önerisi; modül iyi olan anteni kendisi seçer).
8. **İşlemci modül besleme gerilimini ölçer** (arıza teşhisi için).
9. **Kullanılmayanlar:** modülün USB uçları (üretici devre dışı bırakmış), 3,3 V çıkışı (yalnızca ölçüm noktası),
   dört genel amaçlı uç. İki genel amaçlı uç (biri darbe girişi/çıkışı olabilir) ileride kullanım için işlemciye bağlı.
10. **Ortak araçlar:** kutu sembol üreticisine "aynı adlı uçları üst üste koy" seçeneği; ayak izi üreticisine tek ayak
    izi üretme seçeneği eklendi.

## Sahibinin bilmesi gerekenler

- **Frekans ve güç hukuki teyit ister.** Üreticiye göre yalnızca bölge kilitli sürümler uyumluluk belgelidir.
  868 MHz'in AB kilitli sürümü 2 kanalla ve en çok 27 dBm (0,5 W) ile çalışır; yani frekans atlama fiilen yoktur ve
  12 km hedefi bu sürümle ayrıca doğrulanmalıdır. 902-928 MHz sürümü Türkiye'de tahsis gerektirir.
- **Modülün kendi şifrelemesi AES-128'dir** (RFD900x'teki 256 bit seçeneği bu sürümün veri sayfasında yok).
  Operfly'ın uçtan uca şifrelemesi (anahtar güvenli elemanda) bunun üzerinde çalıştığı için güvenlik buna dayanmaz.

## Doğrulanacaklar

- **Ayak izi:** ölçüler veri sayfasındaki tablo ve şekilden çıkarıldı (sütun aralığı 21,2 mm, adım 2,0 mm, anten
  grubunda 1,5 mm, ısı pedleri 8 x 6,6 mm). Kart çiziminden önce üreticinin Altium bileşeniyle karşılaştırılacak.
- **AP63201 çevre elemanları:** geri besleme dirençleri ve 100 pF üretici örnek devresinden (5 V için 158 k / 30,1 k)
  uyarlandı; bobin değeri (10 µH, 500 kHz) hesapla seçildi, üretici tablosuyla ve doyma akımıyla karşılaştırılacak.
- **Isı:** modül verirken yaklaşık 5 W çeker, 1 W yayar; ısı iki orta pedden karta akar. Kart çiziminde ped altına
  geçiş delikleri ve geniş bakır konacak, sürekli verme durumunda sıcaklık ölçülecek.
- **SWO ucu:** 470 ohm üzerinden sıfıra çekmenin yükleme kipine sokmaya yettiği ve normal çalışmada işlemci ucunun
  yüksek empedansta kalması gerektiği denenecek.
- **Anten konnektörü tipi:** modülün kablolu sürümleri ters kutuplu SMA kullanır; kartta düz SMA var. Kullanılacak
  antenlere göre kesinleşecek.
- **Anten hatları:** 50 ohm, kart katman dizilimine göre hesaplanacak (üretici notu).
- **Yazılım:** kanal paketleri, öncelik ve sabit gecikme, bağlantı kaybı bildirimi, modül ayarlarının kilitlenmesi.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_rx.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py RX operfly_rx`.

- **Kart:** 85 x 65 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 82 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 615 yol parçası, 121 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Anten hatları 0,35 mm genişlikte çizildi; 50 ohm empedans üreticinin katman dizilimiyle hesaplanıp doğrulanmadı, hat uzunluğu, kıvrımlar ve geçiş sayısı gözetilmedi. Menzil doğrudan bu hatlara bağlıdır.
- Kenar montajlı SMA konnektörlerinin uçları kart kenarından 0,35 mm içeride başlar; anten hatlarının çevresinde toprak dikiş geçişleri yok.
- Radyo modülünün (RFD900ux-SMT) altındaki bölge ve modül beslemesinin (5,3 V, verici darbelerinde yüksek akım) yolları üretici yerleşim önerisine göre düzenlenmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
