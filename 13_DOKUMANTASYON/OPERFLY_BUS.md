# Operfly Bus (taslak)

Kartlar arası ortak omurga. Durum: taslak — konnektör tipi ve pin sırası henüz kesinleşmedi.

| Katman | İçerik |
| --- | --- |
| Güç | Operfly Power'dan dağıtılan kart beslemesi (gerilim ve akım sınırı belirlenecek) |
| CAN FD | Düğüm keşfi: otomatik düğüm numarası; ad, sürüm ve seri numarası bildirimi |
| Ethernet | 1000BASE-T, PTP (IEEE 1588) destekli anahtar (switch) üzerinden; tüm kameralar Ethernet'tir |

Açık konular: konnektör seçimi, kart dizilimi (üst üste veya kablolu), güç bütçesi.

## Topoloji ve konnektör (14 Kasım 2026 kararları)

- Yıldız topoloji: tüm kartlar Operfly Hub'a bağlanır; diğer kartlarda yalnızca gereken kadar port bulunur.
- Tek standart konnektör: Harwin Gecko-SL, 20 kontak, vida kilitli; araç ve yer cihazlarının tamamında aynı pin sırası.
- Hub her portta elektronik sigorta ve akım ölçümü taşır; sertifikası doğrulanmayan kartın portu veri ağına alınmaz.
- Bilgisayar bağlantısı: Operfly PC adaptörü (Bus konnektörü ↔ USB Type-C, aktif; Ethernet + CAN FD + güvenli eleman).

## Konnektör ve pin planı (14 Kasım 2026)

Konnektör: Harwin Gecko-SL, 1,25 mm, 20 kontak, vida kilitli. Hub port sayısı: 12. Omurga beslemesi: 12 V.
(Önceki askeri dairesel konnektör seçimi maliyet nedeniyle bırakıldı.)

| Sinyal | Pin |
|---|---|
| Gigabit Ethernet (4 çift) | 8 |
| CAN FD A ve B (yedekli) | 4 |
| 12 V (+) | 3 |
| Dönüş (GND) | 4 |
| PPS | 1 |

Kontak başına 2 A (tümü yüklüyken): port başına 6 A, 12 V'ta yaklaşık 70 W. Sızdırmazlık kasa seviyesinde sağlanır.
Motor/servo çıkışları: Gecko-SL 26 kontak.
