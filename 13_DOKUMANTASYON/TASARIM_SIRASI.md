# Tasarım Sırası (14 Kasım 2026)

| Aşama | Ürünler | Amaç |
|---|---|---|
| 1 | Operfly Bus tanımı, Hub, Power, Core, PC adaptörü | Omurga ve uçuş kartı masada çalışır |
| 2 | Nav, Radio, RX, kumanda giriş kartı, Pilot 12, Air, Engine | İlk uçuş: konum, şifreli kumanda ve telemetri |
| 3 | Vision, Range 10/30/100 | GNSS'siz uçuş ve hedef takibi |
| 4 | Cell, Pilot T, Pilot Pro, Base, Ground Radio, Tracker, Shield | Görüntü, 5G, tam yer tarafı, uzun menzil ve karıştırmaya karşı koruma |

Kararlar: Vision modülü Jetson Orin NX (16 GB); Core işlemcisi BGA; batarya, motor ve ESC dışarıdan alınır (2S–12S hazır batarya);
hedef standartlar MIL-STD-810H, MIL-STD-461G, AQAP-2110/2210, STANAG 4609, IPC Sınıf 3.

Bileşen seçimleri (radyo modülü, 5G modülü, mesafe sensörü çekirdekleri, anahtar entegresi)
ilgili aşamanın başında, güncel veri sayfalarıyla doğrulanarak yapılır.

## Hedef araçlar

1. Dört motorlu multikopter, 2 kg faydalı yük, MTOW 30 kg; elektrik tahrik; 6S batarya (şimdilik en büyük), 4'ü 1 arada ESC, motor başına en çok 90 A.
2. Sabit kanat, 10 kg faydalı yük, MTOW 70 kg (şimdilik); benzinli motor, jeneratör + yedek aviyonik bataryası.

Power: omurgada sürekli yaklaşık 150 W, temassız motor akımı algılayıcı girişi (400 A), yedekli servo güç rayı,
jeneratör girişi. Sabit kanat için Air (hava hızı) ve Engine (motor izleme, ateşleme kesme) kartları.
