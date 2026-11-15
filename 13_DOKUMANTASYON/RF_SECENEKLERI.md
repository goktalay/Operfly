# RF Haberleşme: 12 km Tek Standart (14 Kasım 2026)

Önceki dört bant ve beş menzil kademesi bırakıldı. Hazır modüllerle iki bağımsız bağlantı kurulur.

| Bağlantı | Modül | Taşıdığı | Özellikler |
|---|---|---|---|
| Geniş bant | Microhard pMDDL2450 | Video + telemetri | 2,4 GHz, 2x2 MIMO, 1 W, 25 Mbps'ye kadar, mesh, AES |
| Kumanda | RFD900x sınıfı | 12 kanal kumanda + yedek telemetri | 900 MHz bandı, frekans atlamalı, 1 W, AES, çok noktalı |

- Operfly Link ve ayrı radyo/kripto çekirdeği kartı kaldırıldı.
- Radio: geniş bant modül. RX, Pilot 12, Pilot T: kumanda modülü. Pilot Pro ve Ground Radio: ikisi birden.
- Modül şifrelemesinin üzerinde Operfly'ın kendi uçtan uca şifrelemesi çalışır.

Kumanda modülü kararı (15 Kasım 2026, RX şematiği): RFD900x'in karta lehimlenen sürümü RFDesign RFD900ux-SMT
(21 x 29 mm; üretici RFD900x ile uyumlu olduğunu belirtiyor). 868 MHz sürümü RFD868ux-SMT aynı ayak izine oturur;
frekans kararı kart tasarımını değiştirmez. Bu sürümde modülün kendi şifrelemesi AES-128'dir; Operfly'ın uçtan uca
şifrelemesi bunun üzerinde çalışır. Kumandalar ve Ground Radio aynı modülü kullanır.

Bırakılan özellikler: geniş bantta frekans atlama, 1,2 ve 5,2 GHz seçenekleri, 2/4/20/40 km kademeleri,
atlama dizisinin kendi anahtarımızdan türetilmesi.

Açık konular: modül şifrelemesi için ihracat izni, Türkiye'de frekans tahsisi (868 MHz sürümü değerlendirilecek),
ileride frekans atlamalı çok bantlı üst modele (pMDDL1624) geçiş için ayak izi uyumu.
