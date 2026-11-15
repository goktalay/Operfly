# Operfly Pilot Pro ana kartı (OPFKPR)

En üst kumanda modeli: 10 inç ekran, üzerinde çalışan yer istasyonu yazılımı, video ve görüntü işleme (Jetson).
İşlemci ve güvenli eleman taşıyan ortak giriş kartıyla (`01_DONANIM/KUMANDA_GIRIS`) birlikte çalışır; iki kart
arasındaki bağlantı: `13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026): şematikte yalnızca ekran arayüzü eksik

- KiCad projesi: `kicad/operfly_pilotpro.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_PRO operfly_pilotpro`.
- **Çizilenler (ERC 0 hata, 0 uyarı), 7 sayfa:** kök, güç işlemcisi (`dugum`), USB-C güç anlaşması + batarya şarjı
  + güç yolu + 3,3 V / 5 V + güç düğmesi (`guc`), kumanda radyosu + giriş kartı bağlantısı + sesli uyarıcı (`radyo`),
  Jetson soketi + beslemesi + denetimi (`jetson`), NVMe + USB göbeği + dış USB + omurga Ethernet'i + fan (`cevre`),
  geniş bant radyo + ikinci Ethernet portu (`genisbant`).
- **Henüz çizilmeyen:** 10 inç ekranın görüntü ve arka ışık arayüzü (panel seçilmedi). Aşağıda "Sonraki adım"da.
  Bu olmadan kart ürün olarak tamam değildir.
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
9. **Jetson çekirdeği Vision kartıyla aynıdır** (aynı soket, aynı denetim devreleri, aynı sigorta). Fark besleme:
   Jetson'a batarya gerilimi (12-17 V) doğrudan verilir (modül 5-20 V kabul eder); sigorta 10,4 V altında ve
   18,4 V üstünde keser. Jetson'ı güç işlemcisi açar, kapanma isteğini bekleyip düzgün kapatır.
10. **Taşıyıcının 3,3 V'u tek regülatördür (TPS54560B, 5 A)**, batarya geriliminden; NVMe ve ileride ikinci Ethernet
    denetleyicisi içindir. Vision'daki regülatör (en çok 17 V) batarya gerilimine yetmediği için değiştirildi;
    Power ve Cell kartlarındaki parçayla aynıdır.
11. **USB göbeği (4 port):** kumanda işlemcisi, güç işlemcisi, dokunmatik ekran, dış USB-A (bellek, fare, klavye).
    Jetson kapalıyken göbek sıfırlamada tutulur, dış portların 5 V'u kesilir.
12. **USB Type-C tek konnektördür:** hem şarj hem Jetson'ın servis/yazılım yükleme portu (Jetson USB0).
13. **Omurga (Operfly Bus) portu:** Jetson'ın gigabit Ethernet'i + güç işlemcisinin CAN FD hatları. Yer radyosu,
    Base ve bilgisayar buradan bağlanır. Pilot Pro omurgaya güç vermez ve omurgadan güç almaz.
14. **Jetson ↔ güç işlemcisi:** seri port (seviye çeviriciyle) ve USB. Batarya, şarj ve sıcaklık bilgisi buradan gider.
15. **Geniş bant radyo karttadır (Microhard pMDDL2450 OEM)**, Radio kartındaki devrenin aynısıyla: Pilot Pro araçla
    doğrudan video/telemetri bağlantısı kurar, ayrı yer radyosu gerekmez (uzun menzil ve direk üstü anten için
    Ground Radio omurga portundan yine bağlanabilir).
16. **Radyo Jetson'a ikinci bir Ethernet portuyla bağlanır** (Intel I210, Jetson'ın PCIE1 hattı; Vision'daki kamera
    portu devresi). Jetson'ın kendi Ethernet'i omurga portuna ayrıldığı için ikinci port gerekir. Radyonun ve
    denetleyicinin trafoları kart üzerinde sırt sırta bağlanır: iki ayrı kartı kabloyla bağlamanın eşdeğeridir,
    ikisi de üreticilerinin doğrulanmış devresinde kalır.
17. **Radyonun denetim uçları güç işlemcisinin I2C hattındaki küçük genişleticidedir (PCA9536):** sıfırlama, ayar
    kipi, verici beslemesini kesme, "çalışıyor" bilgisi. Güç işlemcisinde boş uç kalmadığı için. Radyonun ayarı
    Jetson'dan Ethernet üzerinden yapılır; seri port yalnızca kurtarma içindir (ölçüm noktaları).

## Sahibinin bilmesi gerekenler

- **Batarya paketi henüz seçilmedi.** Kart 4 hücreli, I2C (SMBus) ölçerli paket bekler; konnektörü ve uç sırası
  seçilen pakete göre kesinleşecek (şematikte yer tutucu 5 uçlu konnektör var).
- **Çalışma süresi:** 100 Wh'lik paketle, 30-35 W ortalama tüketimde yaklaşık 3 saat. Daha uzun süre için ikinci
  paket ya da dış güç (USB-C) gerekir.
- **Şarj süresi:** 60 W'lık USB-C adaptörle yaklaşık 2-2,5 saat; 5 V'luk sıradan USB portundan şarj olur ama çok
  yavaştır ve kumanda açıkken batarya yine de boşalır.
- **STUSB4500'e istenen gerilim üretimde bir kez yazılır** (20 V 3 A); yazılmazsa fabrika ayarıyla daha düşük
  güçte anlaşır. Güç işlemcisi bunu ilk açılışta kendisi yazabilir.
- **Düğmeye uzun basmak (yaklaşık 10 s) gücü ANİDEN keser.** Bu, kilitlenmeye karşı donanım sıfırlamasıdır; Jetson
  için düzgün kapanma değildir ve disk bozulabilir. Olağan kapatma kısa basışladır: güç işlemcisi önce Jetson'ı
  kapatır, sonra gücü keser.
- **Geniş bant radyo tam güçte yaklaşık 9 W, Jetson 15-25 W çeker;** ikisi aynı kasada olduğu için soğutma kasa
  tasarımının en önemli konusudur. Frekans ve güç izinleri Radio kartıyla aynıdır (`01_DONANIM/RADIO/README.md`).
- **Pilot Pro'da yassı kablonun iki ucu farklı kullanılır:** I2C güç işlemcisine gider, PWR_HOLD kullanılmaz.
  Giriş kartının yazılımı kumanda modelini tanıyıp buna göre davranmalıdır (donanımı aynıdır).

## Sonraki adım (henüz çizilmedi)

- **10 inç yüksek parlaklıklı dokunmatik ekran:** panel seçilmedi. Jetson'ın görüntü çıkışı (DP/HDMI) ve arka ışık
  beslemesi panelle birlikte çizilecek; görüntü çıkışının çevre devresi üreticinin tasarım kılavuzuyla
  doğrulanmadan çizilmeyecek. Dokunmatik için USB konnektörü hazır.
- Isıl tasarım ve güç bütçesinin ölçümle doğrulanması (Jetson + radyo + ekran aynı kasada).

## Doğrulanacaklar

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
- **Jetson bölümü** Vision'daki doğrulama listesini devralır (`01_DONANIM/VISION/README.md`): soket parça numarası,
  POWER_EN seviyesi, SYS_RESET ile regülatör açma, USB algılama kutbu üreticinin tasarım kılavuzuyla karşılaştırılacak.
- **SHUTDOWN_REQ bölücüsü** (100k / 22k) batarya gerilimine göre seçildi: 16,8 V'ta 3,0 V, 12 V'ta 2,2 V.
- **3,3 V taşıyıcı regülatörünün kompanzasyonu** (13 kΩ, 4,7 nF, 47 pF) veri sayfası formülleriyle hesaplandı;
  yük adımı ölçümüyle doğrulanacak. Etkinleştirme ucunun 1,8 V'luk SYS_RESET hattına bağlanması numunede denenecek.
- **USB göbeği ayar uçları** (kendi beslemeli, 1. ve 2. portlar çıkarılamaz aygıt) üretici belgesiyle doğrulanacak.
- **USB-C algılama:** VBUS 20 V'a çıkabildiği için algılama transistörünün kapısı 10 V görür (sınır 20 V).
- **Geniş bant radyo bölümü** Radio kartının doğrulama listesini devralır. Ek olarak: modülün RTS girişi boştadır
  (akış denetimi kullanılmaz; modül ayarında kapalı olmalı); 3,3 V'u kartın ortak rayından alır (toplam yük
  ölçülecek); sırt sırta trafo bağlantısında bağlantı hızı ve hata oranı numunede ölçülecek.
- **İkinci Ethernet denetleyicisi** Vision'daki listeyi devralır (taban pedi ölçüsü, ayar belleğinin içeriği).
- **PCA9536** çıkışları açılışta boştadır: sıfırlama ve ayar hatları yukarı çekili, verici beslemesi açık başlar.
