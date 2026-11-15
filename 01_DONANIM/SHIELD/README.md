# Operfly Shield (OPFSHD)

Karıştırma önleyici GNSS anten ürünü (CRPA). Karar: 14 Kasım 2026.

## Sürüm 1 (başlangıç): hazır modül + Operfly arayüz kartı

- Hazır modül: Yunding Antenna YDAJ-P4065 (Çin; satıcı fiyatı 1.342 $). 4 elemanlı CRPA, L1 (BeiDou B1, GPS L1, Galileo E1, GLONASS G1),
  aynı anda 1–3 yön, 65 x 65 x 23,7 mm, en çok 200 g, tipik 5 W / en çok 8 W, 12–36 V besleme; anten ve işlemci tek gövdede.
  Önceki seçim (TUALCOM TUALAJ 4100 MINI) üretici fiyat vermediği için bırakıldı.
- Temizlenmiş RF çıkışı (SMA) Nav kartının anten girişine gider.
- Arayüz kartı: modülü besler, modülün veri konnektöründen durum ve karıştırma bilgisini alıp Operfly Bus'a aktarır;
  OFID ve sertifika taşır.

## Sürüm 2 (sonra): kendi işlem kartımız

- Kart 8 kanala hazır tasarlanır; ilk üretimde 4 kanalı dizilir. Hedef L1 + L5.
- Küçük FPGA + işlemci; Vision takılıysa ek analiz için ham veri Jetson'a da gönderilebilir (isteğe bağlı, zorunlu değil).

Açık konular: modülün veri arayüzü ve mesaj biçimi (satıcıdan arayüz belgesi istenecek); numuneyle performans doğrulaması;
ihracat/ithalat koşullarının teyidi; L1 dışındaki bantlar (çok bantlı RTK için aynı satıcının L1 + L5 modeli YDAJ-P4100D);
sürüm 2 için FPGA/ADC seçimi, kalibrasyon, anten ölçümü.
