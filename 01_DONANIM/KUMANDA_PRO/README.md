# Operfly Pilot Pro ana kartı (OPFKPR)

En üst kumanda modeli: 10 inç ekran, üzerinde çalışan yer istasyonu yazılımı, video ve görüntü işleme (Jetson).
İşlemci ve güvenli eleman taşıyan ortak giriş kartıyla (`01_DONANIM/KUMANDA_GIRIS`) birlikte çalışır; iki kart
arasındaki bağlantı: `13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026): şematik İKİ ADIMDA çiziliyor, 1. adım tamam

- KiCad projesi: `kicad/operfly_pilotpro.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_PRO operfly_pilotpro`.
- **1. adım (tamam, ERC 0 hata, 0 uyarı), 4 sayfa:** kök, güç işlemcisi (`dugum`), USB-C güç anlaşması + batarya
  şarjı + güç yolu + 3,3 V / 5 V + güç düğmesi (`guc`), kumanda radyosu + giriş kartı bağlantısı + sesli uyarıcı
  (`radyo`). Bu kadarıyla kart **kumanda olarak** çalışır (12 kanal, şarj, açma/kapama).
- **2. adım (henüz çizilmedi):** Jetson çekirdeği ve beslemesi, NVMe, Ethernet (omurga portu + geniş bant radyo),
  geniş bant radyo modülü, 10 inç ekran ve dokunmatik arayüzü, USB göbeği. Aşağıda "Sonraki adım" bölümünde.
- Kart çizimi (PCB) başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Kumanda yolu Jetson'dan bağımsızdır.** Çubuk → giriş kartındaki kumanda işlemcisi → kumanda radyosu yolu
   Pilot 12 ile aynıdır. Jetson kilitlense ya da kapalı olsa da araç kumanda edilir. Radyo bağlantısı ve beslemesi
   RX kartındaki ve Pilot 12'deki devrenin aynısıdır (RFD900ux-SMT, ayrı 5,3 V).
2. **Ana kartta ayrı bir güç işlemcisi var (ortak düğüm devresi).** Jetson'ı açıp kapatmak, şarjı ve bataryayı
   izlemek, omurgada (CAN FD) yer birimleriyle konuşmak ve kartın kimliğini kanıtlamak için. Kumanda işlemcisine
   bu işler yüklenmedi: kumanda yolu sade kalır.
3. **Batarya: 4 hücreli (14,4 V) akıllı Li-ion paket**, kendi koruma ve ölçer devresiyle. Gerekçe: Jetson + ekran
   + iki radyo 30-50 W çeker; tek hücreyle olmaz. Hazır akıllı paketler taşıma sertifikalıdır (UN 38.3), kalan
   kapasiteyi kendisi ölçer ve 100 Wh altı seçilirse uçakla taşınabilir. Paketin ölçeri güç işlemcisinin I2C
   hattındadır.
4. **Şarj ve güç yolu: BQ25798** (alçaltan-yükselten). 5-20 V arası her USB-C kaynağından şarj eder; kumanda
   şarjdayken kullanılır; kaynak yetmezse batarya destekler. Entegrenin içinden bataryadan sürekli 6 A, 1 saniye
   10 A geçebilir (12 V'ta 70 W).
5. **USB-C güç anlaşması: STUSB4500** (kendi başına çalışır, yazılım gerektirmez). Kaynakla 20 V'a kadar anlaşır;
   batarya tamamen bitikken de 5 V alıp şarjı başlatır. Devre üreticinin örnek şemasıdır.
6. **Açma / kapama şarj entegresinin batarya anahtarıyla yapılır.** Kapalıyken batarya tümüyle ayrılır (raf ömrü
   uzun). Düğmeye basınca kart açılır; kapatmayı güç işlemcisi yapar (önce Jetson'ı düzgün kapatır). Düğmeye
   yaklaşık 10 s basılı tutmak, yazılımdan bağımsız donanım sıfırlamasıdır (kilitlenmeye karşı).
7. **İki işlemci birbirine doğrudan bağlıdır** (yassı kablodaki I2C hattı ve uyarı ucu): batarya durumu ve
   "kapanıyorum" bilgisi Jetson'a bağlı olmadan kumanda işlemcisine ulaşır (sesli uyarı için).
8. **3,3 V ve 5 V** düğüm kartlarındaki regülatörlerle aynıdır (AP63203 / AP63205), batarya bağlıyken sürekli açıktır.

## Sahibinin bilmesi gerekenler

- **Batarya paketi henüz seçilmedi.** Kart 4 hücreli, I2C (SMBus) ölçerli paket bekler; konnektörü ve uç sırası
  seçilen pakete göre kesinleşecek (şematikte yer tutucu 5 uçlu konnektör var).
- **Çalışma süresi:** 100 Wh'lik paketle, 30-35 W ortalama tüketimde yaklaşık 3 saat. Daha uzun süre için ikinci
  paket ya da dış güç (USB-C) gerekir.
- **Şarj süresi:** 60 W'lık USB-C adaptörle yaklaşık 2-2,5 saat; 5 V'luk sıradan USB portundan şarj olur ama çok
  yavaştır ve kumanda açıkken batarya yine de boşalır.
- **STUSB4500'e istenen gerilim üretimde bir kez yazılır** (20 V 3 A); yazılmazsa fabrika ayarıyla daha düşük
  güçte anlaşır. Güç işlemcisi bunu ilk açılışta kendisi yazabilir.
- **Pilot Pro'da yassı kablonun iki ucu farklı kullanılır:** I2C güç işlemcisine gider, PWR_HOLD kullanılmaz.
  Giriş kartının yazılımı kumanda modelini tanıyıp buna göre davranmalıdır (donanımı aynıdır).

## Sonraki adım (2. adım, henüz çizilmedi)

- Jetson Orin NX soketi ve çekirdek devresi (Vision kartındaki devre temel alınacak), +VSYS'ten sigortalı besleme,
  güç işlemcisiyle açma/kapama, fan.
- NVMe (M.2), USB göbeği (kumanda işlemcisi, güç işlemcisi, dokunmatik ekran, servis USB'si, dış portlar).
- Ethernet: Jetson'ın portu → omurga (Operfly Bus) konnektörü; ikinci port (PCIe denetleyici) → geniş bant radyo.
- Geniş bant radyo modülü (Radio kartındaki devre) ve beslemeleri.
- 10 inç yüksek parlaklıklı dokunmatik ekran arayüzü ve arka ışık beslemesi (panel seçimiyle birlikte).
- Isıl tasarım ve güç bütçesinin ölçümle doğrulanması.

## Doğrulanacaklar (1. adım)

- **Batarya paketi:** konnektör, uç sırası, sıcaklık ucunun türü (şarj entegresi 103AT sınıfı 10 k NTC bekler;
  farklıysa bölücü değişir ya da sıcaklık denetimi paketin kendi korumasına bırakılır), en yüksek şarj akımı.
- **Batarya anahtarı MOSFET'i** (BSC014N04LS) şarj entegresinin çok zayıf kapı sürücüsüyle (100 nA) açılış süresi
  açısından numunede denenecek.
- **Giriş akımı sınırı:** donanım sınırı en yükseğe bağlı; güç işlemcisi anlaşılan akıma göre yazılımla ayarlar.
  Yazılım çalışmadan önce zayıf bir kaynağa bağlanırsa entegrenin giriş gerilimi koruması devreye girer; numunede
  denenecek.
- **STUSB4500 örnek devresindeki anahtarlar** üreticinin önerdiği küçük MOSFET yerine Vision'da kullanılan
  SUD50P04-08 ile çizildi (20 V 3 A'da ısınmaması için); kapı gerilimi 16 V (sınır 20 V). Açılış/kapanış numunede
  ölçülecek.
- **Koruma diyotları** (ESDA25P35-1U1M) için ayak izi yer tutucudur; üretici çizimiyle değiştirilecek.
- **Güç bütçesi ve ısı:** 2. adım tamamlanınca toplam tüketim, bobin ve MOSFET ısısı hesaplanıp ölçülecek.
- Kumanda radyosu ve frekans konuları: `01_DONANIM/KUMANDA_12/README.md` ve `01_DONANIM/RX/README.md`.
