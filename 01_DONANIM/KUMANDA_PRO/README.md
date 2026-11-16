# Operfly Pilot Pro ana kartı (OPFKPR)

En üst kumanda modeli: 10 inç ekran, üzerinde çalışan yer istasyonu yazılımı, video ve görüntü işleme (Jetson).
İşlemci ve güvenli eleman taşıyan ortak giriş kartıyla (`01_DONANIM/KUMANDA_GIRIS`) birlikte çalışır; iki kart
arasındaki bağlantı: `13_DOKUMANTASYON/KUMANDA_ARAYUZU.md`.

## Durum (15 Kasım 2026): şematik tamam, kart çizimi (PCB) başlamadı

- KiCad projesi: `kicad/operfly_pilotpro.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py KUMANDA_PRO operfly_pilotpro`.
- **Çizilenler (ERC 0 hata, 0 uyarı), 8 sayfa:** kök, güç işlemcisi (`dugum`), USB-C güç anlaşması + batarya şarjı
  + güç yolu + 3,3 V / 5 V + güç düğmesi (`guc`), kumanda radyosu + giriş kartı bağlantısı + sesli uyarıcı (`radyo`),
  Jetson soketi + beslemesi + denetimi (`jetson`), NVMe + USB göbeği + dış USB + omurga Ethernet'i + fan (`cevre`),
  geniş bant radyo + ikinci Ethernet portu (`genisbant`), ekran arayüzü: HDMI + 12 V panel beslemesi + parlaklık (`ekran`).
- **Ekran paneli kesin seçilmedi;** bir aday ve bir hedef var (karar 18-20). Kart panele bağlı olmadığı için şematik
  bunu beklemez.
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

18. **Ekran ölçütü (sahibinin talimatı): en yüksek parlaklık, dış ortamda çalışma.** Araştırma (15 Kasım 2026):
    10,1 inçte hazır satılan ürünlerde bulunan en yüksek değer 1500 nit; 2000 nit ve üstü yalnızca özel siparişle
    söyleniyor (teklif ve numune gerekir). Güneşte okunurluk yalnız nit değildir: dokunmatik camın panele optik
    yapıştırılması ve yansıma önleyici kaplama da şarttır; panel şartnamesine bunlar yazılacak.
19. **Kart belirli bir panele bağlı değildir.** Görüntü HDMI ile, besleme 12 V ile, dokunmatik USB ile, parlaklık
    PWM ile verilir. Gerekçe: en parlak panel bugün hazır ürün, yarın özel üretim olabilir; panel değişince kartın
    değişmemesi gerekir. HDMI girişli sürücü kartı hem hazır monitörlerde hem özel panellerde standarttır.
20. **Panel adayı (ilk örnek için): Lilliput TK1019/T.** 1500 nit, 1920 x 1200, 10 noktalı kapasitif dokunmatik,
    ön yüz IP65, HDMI + USB, 12-24 V, en çok 19 W, -20...+70 °C, ortam ışığına göre otomatik karartma. Kasalı bir
    monitördür (264 x 183 x 36 mm): ilk örnekte işi görür, el kumandası için kalın ve ağırdır. **Seri ürün hedefi:**
    aynı arayüzle çalışan açık çerçeve özel panel (1500-2000 nit, optik yapıştırma, yansıma önleyici kaplama).
21. **Görüntü çıkışı HDMI'dır** (Jetson'ın DP1 uçları HDMI kipinde). Devre, üreticinin tasarım kılavuzuna
    (DG-10931, bölüm 9) ve açık kaynaklı bir taşıyıcı kartın üretilmiş HDMI devresine dayanır: her hatta 100 nF,
    499 Ω aşağı çekme (ortak transistörle), ESD dizisi; DDC ve HPD için seviye çevirici; 5 V ucu 0,5 A sınırlı.
    CEC kullanılmaz.
22. **Panel beslemesi: 12 V, 3 A (36 W) ayrı regülatör (TPS54560B; Jetson'ın 3,3 V'undaki parçayla aynı).**
    2000 nit sınıfı bir panele (tahmini 20-25 W) yetecek şekilde boyutlandı. Yalnızca Jetson açıkken çalışır.
    Parlaklık Jetson'dan PWM ile ayarlanır (GPIO13); hazır monitörlerde ayrıca kendi otomatik karartması vardır.

## Sahibinin bilmesi gerekenler

- **Batarya paketi henüz seçilmedi.** Kart 4 hücreli, I2C (SMBus) ölçerli paket bekler; konnektörü ve uç sırası
  seçilen pakete göre kesinleşecek (şematikte yer tutucu 5 uçlu konnektör var).
- **Parlaklık çalışma süresini doğrudan kısaltır.** 1500 nitlik aday panel tam parlaklıkta 19 W'a kadar çeker; bu,
  Jetson'ın kendisi kadardır. 100 Wh'lik paketle kaba tahmin: güneşte tam parlaklıkta 40-45 W ile yaklaşık 2 saat,
  gölgede yarı parlaklıkta 30-35 W ile yaklaşık 3 saat. 2000 nit sınıfı panelle (tahmini 25 W) güneşte 2 saatin
  altına iner. Daha uzun süre için ikinci paket ya da dış güç (USB-C) gerekir. Rakamlar ölçülmedi, tahmindir.
- **Güneş altında panel ısınır.** Koyu yüzey doğrudan güneşte ortam sıcaklığının epey üstüne çıkar; aday panelin
  sınırı 70 °C'dir. Sıcak iklimde (Körfez yazı gibi) bu sınır kasa tasarımında ayrıca ele alınmalıdır.
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

## Sonraki adım

- **Panelin kesinleştirilmesi:** aday monitörden bir numune alınıp güneş altında denenmesi; özel açık çerçeve panel
  için (1500-2000 nit, optik yapıştırma, yansıma önleyici kaplama, HDMI sürücü kartı, 12 V) üreticilerden teklif.
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
- **HDMI devresi:** eşleme, 100 nF, 499 Ω ve seviye çevirici gereği üreticinin tasarım kılavuzundan ve açık kaynaklı
  bir taşıyıcı karttan doğrulandı. Kılavuzdaki örnek şemanın (Şekil 9-6) direnç değerleri metinden okunamadı;
  HPD ve DDC değerleri kart çiziminden önce şekille tek tek karşılaştırılacak. Bilinen açık noktalar:
  DDC hatlarının Jetson tarafı 3,3 V'a çekili (üreticinin kılavuzu 3,3 V, kendi geliştirme kartı 1,8 V gösteriyor);
  HPD tersleyen çeviriciyle bağlı (yazılım ayarı buna göre olmalı); 499 Ω'ların anahtarı modülün uyku ucu yerine
  taşıyıcı 3,3 V'una bağlı (uyku kipi kullanılmıyor); seri dirençler 0 Ω (üretici HDMI 2.0 uyumu için 6 Ω'a kadar
  önerir; görüntü bozulursa 5,1 Ω denenecek).
- **12 V panel regülatörü:** kompanzasyon (13,7 kΩ, 10 nF, 56 pF) veri sayfası formülleriyle, 35 µF etkin çıkış
  kapasitesi varsayımıyla hesaplandı; yük adımı ölçümüyle doğrulanacak. Batarya 12,5 V'un altına inince çıkış
  12 V'un altına düşer (yaklaşık batarya - 0,5 V): seçilen panelin alt gerilim sınırı ve güç işlemcisinin
  kapanma eşiği buna göre belirlenecek (aday monitör 12-24 V ister).
- **Parlaklık PWM'i:** hazır monitörün PWM girişi yoktur (kendi ayarı ve otomatik karartması vardır); PWM ve "aç"
  uçları açık çerçeve panelin sürücü kartı içindir. Frekans ve kutup seçilen sürücü kartına göre ayarlanacak.
- **Fan PWM seviyesi (Vision'dan devralınan devre):** seviye çeviricinin çıkışında kendi 10 kΩ yukarı çekmesi
  vardır; karttaki 10 kΩ aşağı çekmeyle birlikte yüksek seviye 3,3 V'a çıkmaz (yaklaşık 1,7 V). Fanın kendi
  yukarı çekmesi durumu değiştirir; seçilen fanla ölçülecek, gerekirse aşağı çekme 100 kΩ yapılacak.
- **PCA9536** çıkışları açılışta boştadır: sıfırlama ve ayar hatları yukarı çekili, verici beslemesi açık başlar.

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_pilotpro.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py KUMANDA_PRO operfly_pilotpro`.

- **Kart:** 195 x 140 mm, 6 katman (iç 1: toprak, iç 4: +3V3; diğer katmanlar sinyal, elemanlar üstte), 472 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,60/0,30 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim: KART TAMAMLANMADI.** DRC 0 ihlal (-), 1 bağlanmamış uç. Otomatik yol çizici bu kartı bitiremedi;
  kalan bağlantılar elle çizilmeli ya da yerleşim elle düzeltilip yeniden denenmeli.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- Eksik kalan bağlantı: HDMI_D2_K_N (HDMI veri çiftinin bir hattı); elle çizilmeli.
- **Yüksek hızlı hatlar işlevsel sayılmaz:** HDMI, PCIe (NVMe ve Ethernet denetleyicisi), gigabit Ethernet ve USB çiftleri empedans denetimli, eşit uzunlukta ve çift olarak çizilmedi; NVIDIA tasarım kılavuzuna göre elle yeniden çizilmeden ekran, disk ve ağ çalışmayabilir.
- Jetson soketi ve M.2 yuvasının yeri, modüllerin yatacağı bölge, sabitleme delikleri ve soğutucu boşluğu tasarlanmadı; kart ölçüsü ve konnektör yerleri kumanda kasasına göre seçilmedi.
- Şarj devresi (4S, USB güç aktarımı), batarya anahtarı ve regülatörlerin (Jetson 4 A, panel 3 A) güç yolları dar çizildi; geniş bakırla yeniden çizilmeden kart tam yükte kullanılmaz.
- Anten hatları 0,35 mm çizildi, empedansı doğrulanmadı; geniş bant modülünün (7,5 W) soğutması tasarlanmadı.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
