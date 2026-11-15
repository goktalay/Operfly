# Kumanda iç arayüzü (15 Kasım 2026)

Kumandaların içinde iki kart vardır: **giriş kartı** (üç modelde ortak) ve **ana kart** (modele özel).
Bu belge ikisi arasındaki bağlantıyı tanımlar. Kaynak: `01_DONANIM/KUMANDA_GIRIS/kicad/uret.py`.

## Görev dağılımı

| Kart | Taşıdıkları |
|---|---|
| Giriş kartı | Kumandanın gerçek zamanlı işlemcisi (STM32G0B1CET6), güvenli eleman, çubuk/tekerlek/anahtar/düğme girişleri, ekran-genişleme konnektörü, iki durum ışığı |
| Ana kart | Batarya, şarj ve güç anahtarlama, 3,3 V ve radyo beslemesi, kumanda radyo modülü ve antenleri, USB Type-C, sesli uyarıcı; üst modelde ayrıca Jetson, geniş bant radyo ve ekran |

Kumanda yolu (çubuk → işlemci → şifreleme → kumanda radyosu) yalnızca giriş kartındaki işlemciden geçer.
Pilot Pro'da Jetson bu yolun üzerinde değildir; çubuk verisini USB üzerinden ayrıca alır.

## Konnektör

20 kontaklı yassı kablo (FFC), 0,5 mm adım; kart tarafı Hirose FH12-20S-0.5SH. Besleme ana karttan gelir.
Kablonun kontak yönü (aynı yön / ters yön) ana kartın çiziminde kesinleşir; 1 numaralı uç her iki kartta aynı sinyaldir.

| Uç | Sinyal | Yön (giriş kartına göre) | Açıklama |
|---|---|---|---|
| 1 | GND | | |
| 2 | +3V3 | giriş | Ana karttan 3,3 V; giriş kartı en çok 0,3 A çeker (ekran dahil) |
| 3 | +3V3 | giriş | |
| 4 | GND | | |
| 5 | RADIO_RXD | çıkış | İşlemci → kumanda radyosu veri girişi (3,3 V) |
| 6 | RADIO_TXD | giriş | Kumanda radyosu veri çıkışı → işlemci |
| 7 | RADIO_CTS | çıkış | İşlemcinin "gönderebilirsin" çıkışı → radyonun CTS girişi |
| 8 | RADIO_RTS | giriş | Radyonun RTS çıkışı → işlemci |
| 9 | RADIO_OFF | çıkış | 1: radyo beslemesi kapalı. Giriş kartında 100 k aşağı çekili (sıfırlamada radyo açık) |
| 10 | RADIO_BOOT_N | çıkış, açık kollektör | 0 iken radyo beslemesi açılırsa modül yazılım yükleme kipine girer. Giriş kartında 10 k yukarı çekili |
| 11 | GND | | |
| 12 | USB_DM | iki yönlü | İşlemcinin USB'si (tam hız); ana karttaki Type-C konnektöre ya da Jetson'a |
| 13 | USB_DP | iki yönlü | |
| 14 | GND | | |
| 15 | I2C_SCL | çıkış | Ana karttaki batarya ölçer ve benzeri aygıtlar. Yukarı çekmeler (2,2 k) giriş kartındadır |
| 16 | I2C_SDA | iki yönlü | |
| 17 | ALERT_N | giriş | Ana karttaki aygıtların ortak uyarı çıkışı (açık kollektör). Giriş kartında 10 k yukarı çekili |
| 18 | PWR_BTN_N | giriş | Güç düğmesi basılıyken 0. Giriş kartında 100 k yukarı çekili |
| 19 | PWR_HOLD | çıkış | 1: işlemci beslemeyi açık tutar. Giriş kartında 100 k aşağı çekili |
| 20 | BUZZER | çıkış | Sesli uyarıcı için darbe genişlik çıkışı (3,3 V lojik; sürücü transistörü ana karttadır) |

Ana kart kuralları:

- Radyo veri hatlarına ana kartta, modülün yanında 470 ohm seri direnç konur (RX kartındaki gibi).
- I2C hatlarına ana kartta ikinci bir yukarı çekme konmaz.
- USB hatları ana kartta koruma elemanından geçer; giriş kartında koruma yoktur.
- Güç açma: düğmeye basılınca ana kart beslemeyi açar; işlemci PWR_HOLD'u 1 yapınca besleme düğme bırakılsa da
  sürer. Kapatma: işlemci PWR_HOLD'u 0 yapar.

## Giriş konnektörleri (giriş kartında, JST-GH 1,25 mm)

Uç sıraları Operfly tanımıdır; satın alınan çubuk ve anahtarların kabloları bu sıraya göre hazırlanır.

| Konnektör | Adet | Uçlar |
|---|---|---|
| Çubuk (gimbal) | 2 | +3V3A, X, Y, GND |
| Tekerlek | 2 | +3V3A, sinyal, GND |
| Anahtar (2 ya da 3 konumlu) | 6 | +3V3A, ortak uç, GND |
| Yön tuşu (5 yönlü) | 1 | GND, orta, yukarı, aşağı, sol, sağ |
| Düğme | 2 | sinyal, GND |
| Ekran / genişleme | 1 | +3V3, GND, SCK, MOSI, MISO, CS, DC, RST, BL, GND |

12 kumanda kanalı: 4 çubuk ekseni + 2 tekerlek + 6 anahtar. Düğmeler ve yön tuşu kanal sayılmaz.
