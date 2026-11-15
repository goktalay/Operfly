# Operfly Cell (OPFCEL)

5G hücresel bağlantı kartı: telemetri ve görüntü için ikinci haberleşme yolu. Kart hazır bir M.2 5G modemi taşır,
besler ve onu omurganın Ethernet'ine bağlar.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_cell.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py CELL operfly_cell`.
- Şematik tamam, 4 sayfa: kök, düğüm (`dugum`), modem (`modem`), Ethernet (`ethernet`). ERC 0 hata, 0 uyarı.
  Kart çizimi başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Modem hazır M.2 modüldür; aday Quectel RM520N-GL** (M.2 Key B, 30 × 52 mm). 5G'nin n28 ve n78 bantlarını
   (Türkiye) ve 4G'yi destekler; 5G yoksa 4G'ye düşer. Uç sıraları üreticinin donanım tasarım kılavuzundan alındı
   (RM520N-GL Hardware Design V1.0, Tablo 5).
2. **Veri yolu: modem → PCIe → karttaki Ethernet denetleyici → omurga Ethernet'i.** Modem PCIe'yi "kök" kipinde
   çalıştırır ve karttaki gigabit Ethernet denetleyiciyi (Realtek RTL8111H) kendisi sürer; kart omurgaya sıradan bir
   Ethernet cihazı olarak çıkar. Gerekçe: düğüm işlemcisi (USB tam hız, 12 Mbit) görüntü trafiğini taşıyamaz;
   omurganın yüksek hızlı yolu Ethernet'tir. Piyasadaki "5G modem → Ethernet" kartları da aynı yapıyı kullanır.
3. **Düğüm işlemcisi veri taşımaz, modemi yönetir:** beslemeyi açar/kapatır, modemi kurallı biçimde kapatır,
   sıfırlar, uçak kipine alır; USB üzerinden AT komutlarıyla sinyal gücünü, şebeke kaydını ve SIM seçimini okur ve
   omurgadan (CAN FD) bildirir. Böylece 5G bağlantısının durumu uçuş bilgisayarına Ethernet'ten bağımsız ulaşır.
4. **Modemin USB'si bir anahtarla (FSUSB42) iki yere verilir:** kablo takılı değilken düğüm işlemcisine, servis
   USB'sine (Type-C) kablo takılınca bilgisayara. Modem yazılımı yalnızca USB'den güncellenebildiği için servis
   portu zorunludur.
5. **Modem beslemesi ayrı regülatördür: 3,8 V / 5 A (TPS54560B, omurga 12 V'undan).** Modem 3,135–4,4 V ister ve
   verici patlamalarında 3 A çeker; üretici en az 3 A sürekli akım, 2 × 220 µF düşük ESR kondansatör, seramik dizi
   ve 5 V kırpma diyodu ister (hepsi kartta). Regülatör Power kartındaki servo regülatörüyle aynı parçadır.
6. **Giriş alt gerilim kilidi:** regülatör 9,0 V'ta açar, 8,0 V'ta kapatır (omurga çökerken modem açılıp kapanmaz).
7. **Ethernet denetleyicinin 3,3 V'u ayrıdır (TPS62130, 5 V'tan)** ve modem beslemesi gelince açar. Modem
   beslemesi yokken denetleyici ve PCIe yukarı çekme dirençleri de gerilimsiz kalır; kapalı modemin uçlarına
   gerilim verilmez.
8. **İki nano-SIM yuvası (çift operatör).** Modem aynı anda birini kullanır; diğerine AT komutuyla geçilir.
   Kart algılama (sıcak takma) kullanılmaz. İkinci yuvanın hatlarında üreticinin önerdiği 0 Ω dirençler var: dahili
   eSIM'li modem sürümü takılırsa bu dirençler dizilmez.
9. **Lehimli eSIM bu revizyonda yok.** Lehimli eSIM yongasının uç sırası burada doğrulanamadı ve operatör profili
   sözleşmesi gerektirir; ikinci nano-SIM yuvası aynı işi görür (nano-SIM biçiminde eSIM kartları da takılabilir).
10. **Antenler modülün kendi konnektörlerinden çıkar** (4 adet, ince koaksiyel kabloyla kasadaki SMA'lara). Kartta
    RF izi yoktur; kartın RF tasarımı ve ölçümü gerekmez.
11. **Modemin konum alıcısı kullanılmaz;** konum Nav kartından gelir.

## Sahibinin bilmesi gerekenler

- **Modem ayrı satın alınır** ve yuvaya takılır; SIM kartlar (ya da eSIM profili) operatörden alınır.
- **İlk kurulumda modem bir kez ayarlanır** (servis USB'sinden ya da düğüm işlemcisinden AT komutlarıyla): PCIe kök
  kipi ve Ethernet denetleyici sürücüsü açılır. Bu ayarlar modemde kalıcıdır; üretimde otomatikleştirilecek.
- **Servis USB'si kartı beslemez.** Modem ayarlanırken ya da güncellenirken kart omurgadan beslenmelidir.
- **Besleme modem kapatılmadan kesilmemelidir.** Üretici, modem kapatma ucuyla kapatılıp yaklaşık 1 s beklenmeden
  beslemenin kesilmesinin modemin belleğini bozabileceğini yazar. Düğüm yazılımı bunu sırayla yapar; uçakta ana
  şalter aniden kapatılırsa bu kural çiğnenir (aşağıda "Doğrulanacaklar").
- **Modem ısınır;** üretici çalışma sıcaklığı aralığı (−30…+75 °C) için soğutma ister. Kasada modemin altına ısı
  dolgusu ve soğutucu gerekir.
- **Güç:** tepe yaklaşık 11 W (12 V'ta 1 A), ortalama birkaç watt. Hub portunun 6 A sınırı içinde.
- **Havada 5G/4G kapsaması yerdeki gibi değildir:** baz istasyonu antenleri yere bakar; yükseldikçe bağlantı
  bozulabilir ve bir cihazın havadan şebekeyi kullanması operatör koşullarına bağlıdır. Cell bu yüzden *ikinci*
  haberleşme yoludur, birincisi değil.
- **Trafik şifreli tünelden geçer** (kartın sertifikasıyla); bu yazılım işidir, donanımda ek parça gerektirmez.

## Doğrulanacaklar

- **Modemin Ethernet denetleyici desteği yazılım sürümüne bağlıdır.** PCIe kök kipi üreticinin kılavuzunda var
  (uç tablosu dipnotu ve AT komutu); RTL8111H sürücüsünün modem yazılımında bulunduğu ise yalnızca kullanıcı
  forumlarından biliniyor. Numune modemle denenecek; gerekirse üreticiden doğru yazılım sürümü istenecek.
  Olmazsa aynı ayak izi ailesinden RTL8125B'ye geçiş (2,5 Gbit) değerlendirilecek.
- **Ethernet denetleyicinin çevre değerleri** (RSET 2,49 kΩ, 1,0 V çıkış kondansatörleri, ISOLATEB bölücüsü, LED
  uçları, kristal yük kondansatörleri) üreticinin başvuru şematiğinden değil, aynı ailenin yaygın uygulamalarından
  alındı; veri sayfası bu değerleri vermiyor. Realtek başvuru şematiğiyle karşılaştırılacak.
- **Ethernet denetleyicinin MAC adresi** entegrenin bir kez yazılır belleğinde durur; boş entegrede adresin nasıl
  atanacağı (üretimde yazma ya da modem tarafında atama) netleşecek.
- **Ayak izleri:** RTL8111H alt ped ölçüsü ve M.2 yuvasının yüksekliği/vida yeri (30 × 52 mm modül) üretici
  çizimleriyle doğrulanacak.
- **Regülatör kompanzasyonu** (26,7 kΩ, 15 nF, 220 pF) veri sayfasındaki formüllerle hesaplandı; üreticinin tasarım
  aracıyla ve yük adımı ölçümüyle doğrulanacak. Modem patlamalarında gerilim düşüşü ve dalgalanma (< 100 mV) ölçülecek.
- **Ani besleme kesilmesi:** modemin kurallı kapanması için 1 s'lik enerji deposu (süper kondansatör) gerekip
  gerekmediği numunede denenecek.
- **Düğüm işlemcisinin USB ana bilgisayar kipi:** aşağı çekme dirençlerinin işlemcinin içinde olduğu varsayıldı;
  kartta dizilmeyen 15 kΩ yerleri bırakıldı. Modemin tam hızda (12 Mbit) tanınması numunede denenecek.
- **Cihaz kaydı ve operatör uyumluluğu:** modülün Türkiye'de kullanım onayı, IMEI kaydı, operatörlerin bant ve
  hizmet (havadan kullanım, sabit IP/APN) koşulları teyit edilecek.
- **Şifreleme için ihracat/ithalat koşulları** ve modülün menşe/ihracat sınıfı teyit edilecek.
- **Çalışma sıcaklığı:** modül −40 °C'ye kadar "genişletilmiş" aralıkta çalışır ama başarımı garanti etmez; askeri
  sıcaklık aralığı hedefi için değerlendirilecek.
