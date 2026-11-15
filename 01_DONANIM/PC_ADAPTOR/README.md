# Operfly PC adaptörü (OPFPCA)

Bilgisayarı omurgaya bağlar: USB Type-C tarafında gigabit Ethernet ve CAN FD; kendisi de sertifikalı bir Operfly kartıdır.

## Durum (15 Kasım 2026)

- KiCad projesi: `kicad/operfly_pc_adaptor.kicad_pro`.
  Üretim ve denetim: `python 10_ORTAK_ARACLAR/kicad/denetle.py PC_ADAPTOR operfly_pc_adaptor`.
- Şematik tamam, 4 sayfa: düğüm (`dugum`), USB/göbek/beslemeler (`usb`), Ethernet köprüsü (`ethernet`).
  ERC 0 hata, 0 uyarı. Kart çizimi başlamadı.

## Kararlar (sahibi kararı tasarımcıya bıraktı)

1. **Tek USB Type-C kablosu, içeride USB göbeği** (USB2514B). 1. portunda Ethernet köprüsü, 2. portunda düğüm
   işlemcisinin USB'si (CAN FD geçidi ve kimlik doğrulama) var. Bilgisayar iki aygıt görür; tek kablo yeter.
2. **Ethernet köprüsü LAN7500i** (USB 2.0 yüksek hız, gigabit Ethernet). Bağlantıları üreticinin şematik denetim
   listesine göre yapıldı. USB 2.0 hattı gerçek veri hızını yaklaşık 300-400 Mbit/s ile sınırlar; yapılandırma,
   kayıt indirme ve canlı izleme için yeterlidir. USB 3 köprüsü sonraki revizyon seçeneğidir.
3. **Kart USB'den beslenir, omurgaya 12 V vermez.** Bağlandığı kart kendi beslemesini taşır. Tahmini tüketim 2 W
   civarı (5 V'ta yaklaşık 0,4 A); standart USB 2.0 portunun 0,5 A sınırına yakındır, bu yüzden Type-C ya da
   USB 3 portu önerilir.
4. **Beslemeler:** 5 V'tan 3,3 V ve 1,2 V (iki TPS62130). Köprünün içinde regülatör yoktur.
5. **CAN sonlandırması 120 ohm dizili.** Adaptör tek karta doğrudan bağlandığında hat bu dirençle sonlanır.
   Hub'a bağlandığında toplam yük yaklaşık 40 ohm olur (sınırda; ölçülecek, gerekirse direnç sökülür).
6. **Köprünün MAC adresi için EEPROM yok;** adres yazılımdan verilir. Şartname gereği dış ağa çıkan üründe resmi
   adres bloğu gerekir; kalıcı adres için EEPROM sonraki revizyonda eklenecek.
7. **Sıfırlama:** 3,3 V yaklaşık 3,0 V'u geçene kadar göbek ve köprü sıfırda tutulur.
8. **Göbeğin kullanılmayan 3. ve 4. portları kapalı** (üreticinin önerdiği 10 k yukarı çekmelerle).

## Doğrulanacaklar

- USB2514B ayar kayışları (veri yolundan beslenen çalışma, 1. ve 2. portların çıkarılamaz işaretlenmesi) üretici
  belgesindeki tabloyla karşılaştırılacak.
- LAN7500i: kullanılmayan JTAG, GPIO ve EEPROM uçlarının bağlanma önerisi; kristal yük kondansatörleri (15-33 pF aralığı).
- TPS62130 ve TPS3808 ayrıntıları (Hub ve Core doğrulama listeleriyle ortak).
- Toplam USB akımı ölçülecek.
