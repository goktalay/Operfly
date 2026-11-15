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

## Kart çizimi (otomatik)

Sahibinin kararıyla kart **otomatik** çizildi: yerleşim `pcb_yerlesim.py`, yollar dış bir otomatik yol çiziciyle
(`pcb_ciz.py`). Dosya: `kicad/operfly_pc_adaptor.kicad_pcb`; ayarlar `kicad/pcb_ayar.py`.
Yeniden üretmek için: `python 10_ORTAK_ARACLAR/kicad/pcb_ciz.py PC_ADAPTOR operfly_pc_adaptor`.

- **Kart:** 80 x 55 mm, 4 katman (üst: elemanlar + sinyal, iç 1: toprak, iç 2: +3V3, alt: sinyal), 140 eleman, tamamı üst yüzde; köşelerde M3 montaj deliği.
- **Kurallar:** yol 0,20 mm, açıklık 0,125 mm, geçiş 0,6/0,3 mm; besleme ağları, ağın en dar ucunu aşmayacak biçimde 0,2-1,0 mm (0,4 mm ve üstünde geçiş 0,8/0,4 mm); bakır-kenar 0,25 mm.
- **Denetim:** DRC 0 ihlal, 0 bağlanmamış uç; şematik-kart uyumu temiz. 1157 yol parçası, 218 geçiş.

**Bu bir mühendis çizimi değildir.** Üretimden önce bir kart tasarımcısının bakması gereken noktalar:

- USB 2.0 çiftleri (Type-C → göbek → Ethernet denetleyicisi ve işlemci) ile gigabit Ethernet çiftleri 90/100 ohm fark empedansında ve eşit uzunlukta çizilmedi; bağlantı kurulsa bile hız düşebilir ya da hata verebilir.
- Ethernet denetleyicisinin (LAN7500i) 1,2 V çeviricisi, kristalleri ve trafo çevresi üretici yerleşim önerisine göre düzenlenmedi.
- Anahtarlamalı regülatörlerin (bobin, diyot, giriş/çıkış kondansatörleri) akım döngüleri küçük tutulmadı; gürültü ve verim ölçülmeli.
- Kristal ve osilatör hatları en kısa yoldan çizilmedi; altlarından başka sinyal geçip geçmediğine bakılmalı.
- Fark çiftleri (CAN, USB, Ethernet) çift olarak, eşit uzunlukta ve empedans denetimli çizilmedi.
- Güç elemanlarının soğutma bakırı ve ısıl geçişleri ayrıca hesaplanmadı.
- Eleman adları üretim katmanında bırakıldı; kart üstünde yazı (serigrafi) yok.
- Kasa, konnektör yerleri ve montaj delikleri mekanik tasarımla eşleştirilmedi.
- Üretim dosyaları (Gerber, delik, dizgi) henüz çıkarılmadı.
