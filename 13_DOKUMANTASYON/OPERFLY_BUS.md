# Operfly Bus

Kartlar arası ortak omurga: tek konnektörde güç, yedekli CAN FD, Ethernet ve PPS.

| Katman | İçerik |
| --- | --- |
| Güç | Operfly Power'dan gelen 12 V; Hub her portta elektronik sigorta ve akım ölçümü taşır |
| CAN FD (A ve B) | Düğüm keşfi, durum ve yönetim; iki bağımsız hat |
| Ethernet | 1000BASE-T, PTP (IEEE 1588) destekli; Core bu ağa 100 Mbit ile bağlanır |
| PPS | Nav'dan gelen saniye darbesi |

## Topoloji ve konnektör (14 Kasım 2026 kararları)

- Yıldız topoloji: tüm kartlar Operfly Hub'a bağlanır; diğer kartlarda yalnızca gereken kadar port bulunur.
- Tek standart konnektör: Harwin Gecko-SL, 20 kontak, vida kilitli; araç ve yer cihazlarının tamamında aynı pin sırası.
- Hub her portta elektronik sigorta ve akım ölçümü taşır; sertifikası doğrulanmayan kartın portu veri ağına alınmaz.
- Bilgisayar bağlantısı: Operfly PC adaptörü (Bus konnektörü ↔ USB Type-C, aktif; Ethernet + CAN FD + güvenli eleman).

## Konnektör ve pin planı (14 Kasım 2026)

Konnektör: Harwin Gecko-SL, 1,25 mm, 20 kontak, vida kilitli. Hub port sayısı: 12. Omurga beslemesi: 12 V.
(Önceki askeri dairesel konnektör seçimi maliyet nedeniyle bırakıldı.)

Pin planı (15 Kasım 2026). Pin n ile pin n+10 karşı karşıyadır; diferansiyel çiftler karşılıklı pinlerdedir.

| Sütun | Üst sıra | Sinyal | Alt sıra | Sinyal |
|---|---|---|---|---|
| 1 | 1 | +12V | 11 | +12V |
| 2 | 2 | +12V | 12 | GND |
| 3 | 3 | GND | 13 | GND |
| 4 | 4 | CAN_A_H | 14 | CAN_A_L |
| 5 | 5 | CAN_B_H | 15 | CAN_B_L |
| 6 | 6 | PPS | 16 | GND |
| 7 | 7 | ETH_A+ | 17 | ETH_A- |
| 8 | 8 | ETH_B+ | 18 | ETH_B- |
| 9 | 9 | ETH_C+ | 19 | ETH_C- |
| 10 | 10 | ETH_D+ | 20 | ETH_D- |

- Güç bir uçta, Ethernet diğer uçtadır; PPS/GND sütunu CAN ile Ethernet'i ayırır.
- 100 Mbit çalışan kartlar (Core) yalnızca A ve B çiftlerini kullanır.
- Kart tarafı konnektör: Harwin Gecko-SL G125-MS12005M2P (erkek, dik, SMT, vida kilitli).
- KiCad sembolü: `01_DONANIM/ORTAK_KUTUPHANE/semboller/operfly.kicad_sym` içinde `Operfly_Bus_20`.
- Pin sırası numune kablo ile gigabit ölçümünden sonra kesinleşir.

Kontak başına 2 A (tümü yüklüyken): port başına 6 A, 12 V'ta yaklaşık 70 W. Sızdırmazlık kasa seviyesinde sağlanır.
Motor/servo çıkışları: Gecko-SL 26 kontak.
