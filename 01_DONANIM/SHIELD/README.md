# Operfly Shield — karıştırma önleyici anten birimi (OPFSHD), sürüm 1

Karıştırmaya (jamming) karşı korumalı GNSS anteni. Temizlenmiş sinyali Nav'a verir. Sürüm 1: hazır 4 elemanlı
L1 modülü (Yunding Antenna YDAJ-P4065) + bu klasördeki Operfly arayüz kartı. Sürüm 2 (kendi işlem kartımız) ayrıdır.

Ürün kararı 14 Kasım 2026'da verildi. Önceki modül seçimi (TUALCOM TUALAJ 4100 MINI) üretici fiyat vermediği için
bırakıldı; modül Çin'den ya da yurt dışından satın alınabilenler arasından seçildi.

## Durum (15 Kasım 2026): arayüz kartının şematiği tamam, kart çizimi (PCB) başlamadı

- KiCad projesi: `kicad/operfly_shield.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py SHIELD operfly_shield`.
- **Çizilenler (ERC 0 hata, 0 uyarı), 3 sayfa:** kök, düğüm devresi (`dugum`), modül beslemesi + seri arayüz +
  modül konnektörü (`modul`).
- **Modülün arayüz belgesi elimizde yok.** Üretici sayfasında yalnızca besleme aralığı, güç, ölçü ve konnektör
  türleri yazıyor; seri arayüzün türü ve konnektörün uç sırası yazmıyor. Kart bu bilinmeyenlere göre esnek çizildi
  (karar 4 ve 5); ara kablo belge gelince hazırlanacak.
- Kart çizimi (PCB) başlamadı.

## Modül hakkında doğrulananlar (üretici sayfası, 15 Kasım 2026)

- 4 elemanlı; BDS B1, GPS L1, Galileo E1, GLONASS G1; aynı anda 1–3 karıştırıcı yönü.
- Besleme 12–36 V DC; tipik en çok 5 W, karıştırma önleme etkinken en çok 8 W.
- İçinde alıcı var: konum çözümü de verebilir; karıştırmadan arındırılmış RF çıkışı da verir.
- Konnektörler: J30J-9ZK (besleme ve veri) + SMA-K (RF çıkışı).
- 65 × 65 × 23,7 mm, en çok 200 g, −40…+70 °C. Fiyat 1.342 $.
- Anten ve işlemci tek gövdededir. Aynı satıcının L1 + L5 modeli (YDAJ-P4100D) çok bantlı kullanım için adaydır.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Arayüz kartı bir düğümdür:** modülü besler, durumunu izler, seri arayüzünü omurgaya (CAN) taşır ve birimin
   kimliğini kanıtlar. RF yolu karttan geçmez: modülün RF çıkışı koaksiyel kabloyla doğrudan Nav'ın anten girişine gider.
2. **Modül 18 V ile beslenir (yükselten regülatör, TPS61175).** Gerekçe: modül en az 12 V ister; omurganın 12 V'u
   giriş diyodu ve kablo düşümünden sonra bu sınırın altında kalabilir. 18 V, 12–36 V aralığının güvenli bir
   noktasıdır. Regülatör 3 A anahtarlıdır, 8 W'lık yük için geniş paya sahiptir; değerler üreticinin tipik
   uygulamasındandır.
3. **Modül beslemesi sigortalı ve anahtarlıdır; sıfırlamada AÇIKTIR.** İşlemci yeniden başlasa da konum kesilmez.
   İşlemci gerekirse modülü kapatıp açabilir (kilitlenmeye karşı). Modül gerilimi ölçülür.
4. **Seri arayüz RS-232 varsayıldı, 3,3 V seçeneği bırakıldı.** Aynı sınıftaki ürünlerde arayüz RS-232'dir; bu
   modül için doğrulanmadı. Kartta RS-232 alıcı-verici (MAX3232) ve dizgi seçeneğiyle doğrudan 3,3 V yolu vardır:
   belge gelince kart yeniden çizilmeden doğru seçenek dizilir.
5. **Kart tarafındaki modül konnektörü Operfly tanımıdır** (JST-GH 6: 1–2 +18 V, 3–4 GND, 5 kart → modül,
   6 modül → kart). Modülün kendi konnektörüne giden ara kablo, satıcı uç sırasını bildirince hazırlanır.
6. **Modülün kendi konum çıktısı yedek kaynak olarak omurgaya aktarılır;** asıl konum Nav'dadır.

## Sahibinin bilmesi gerekenler

- **Satıcıdan arayüz belgesi istenmeli:** konnektörün uç sırası, seri arayüzün türü (RS-232 / RS-422 / 3,3 V),
  hızı ve veri biçimi, RF çıkışının seviyesi, RF çıkışına doğru gerilim verilip verilemeyeceği. Bu belge gelmeden
  ara kablo yapılmaz ve modül karta bağlanmaz.
- **Nav'ın anten beslemesi (3,3 V) bu modülle KAPALI tutulmalıdır**, modülün RF çıkışının doğru gerilime dayandığı
  doğrulanana kadar. Gerekirse araya doğru gerilim engelleyici konur.
- **RF seviyesi:** aynı sınıftaki bir üründe çıkış seviyesi normal bir antene göre çok yüksek veriliyor. Bu modülde
  de öyleyse Nav girişine zayıflatıcı gerekebilir; numunede ölçülecek.
- **Modül yalnızca L1 bandında çalışır.** Nav'ın çok bantlı RTK doğruluğu Shield takılıyken tek banda iner;
  çok bantlı model ayrıca değerlendirilecek.
- **Performans üretici beyanıdır;** numuneyle gerçek karıştırıcı altında doğrulanmalıdır. İhracat ve ithalat
  koşulları hukuki teyit ister.
- **Modül 5–8 W ısı üretir** ve aracın üstünde, güneş altında durur; montaj yüzeyi ısıyı almalıdır.

## Doğrulanacaklar

- **Seri arayüz:** RS-232 varsayımı; RS-422 çıkarsa alıcı-verici değişir (kart çiziminden önce netleşmeli).
- **Yükselten regülatör:** kompanzasyon (10 kΩ + 22 nF) ve yumuşak kalkış (47 nF) üreticinin tipik uygulamasındaki
  değerlerdir (5 V → 24 V için verilmiş); 12 V → 18 V, 0,45 A için yük adımı ölçümüyle doğrulanacak. Alt ped ölçüsü
  üretici çizimiyle karşılaştırılacak. Regülatörün gürültüsünün GNSS bandına etkisi numunede ölçülecek.
- **Anahtar MOSFET'i** (DMP3099L, 30 V): 18 V'ta kapı gerilimi 9 V'a bölündü; açılış akımı (modülün giriş
  kondansatörü) numunede ölçülecek.
- **Omurga gerilimi 16 V'a çıkarsa** (yer tarafında dış beslemeyle) regülatör çıkışı yine 18 V'tur; giriş 18 V'u
  geçmemelidir (omurganın kırpma diyodu 18 V).
- **Modülün açılış süresi ve işlemci yeniden başladığında davranışı** numunede denenecek.

## Sürüm 2 (sonra): kendi işlem kartımız

- Kart 8 kanala hazır tasarlanır; ilk üretimde 4 kanalı dizilir. Hedef L1 + L5.
- Küçük FPGA + işlemci; Vision takılıysa ek analiz için ham veri Jetson'a da gönderilebilir (isteğe bağlı, zorunlu değil).
- Açık konular: FPGA ve ADC seçimi, kalibrasyon, anten ölçümü, ihracat denetimi teyidi.
