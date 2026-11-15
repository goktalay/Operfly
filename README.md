# OPERFLY

Operfly (Operational Flight), bir uçuş için gereken tüm kartların ve yazılımın tek ekosistem olarak
tasarlandığı kapalı bir sistemdir: uçuş kartları, kartlar arası omurga (Operfly Bus), gömülü yazılım,
kiracılı (çok kurumlu) merkez ve yer istasyonu. Operfly bileşenleri yalnızca birbirleriyle çalışır.

> **Bu depo özeldir (private).** Sır, özel anahtar, parola, canlı veritabanı dökümü veya müşteri verisi
> depoya eklenmez. Üretim çıktıları (gerber, kurulum paketleri) depoda değil, Releases altındadır.

## Ürünler

| Kod | Ad | İşlev | Kaynak |
|---|---|---|---|
| **OPFCOR** | Operfly Core | Uçuş kontrol kartı | `01_DONANIM/CORE/` |
| **OPFPWR** | Operfly Power | Batarya girişi, kart beslemeleri, akım/gerilim ölçümü | `01_DONANIM/POWER/` |
| **OPFVIS** | Operfly Vision | Görüntü işleme kartı (Jetson taşıyıcı, yalnızca Ethernet kamera) | `01_DONANIM/VISION/` |
| **OPFRAD** | Operfly Radio | Geniş bant radyo kartı: video + telemetri (2,4 GHz, 12 km, şifreli, mesh) | `01_DONANIM/RADIO/` |
| **OPFNAV** | Operfly Nav | GNSS kartı (RTK, karıştırma/aldatma tespiti) | `01_DONANIM/NAV/` |
| **OPFTRK** | Operfly Tracker | Anten takip birimi (yer tarafındaki yönlü anteni araca çevirir) | `01_DONANIM/TRACKER/` |
| **OPFSHD** | Operfly Shield | Karıştırma önleyici GNSS anteni: hazır 4 kanallı L1 CRPA modülü + arayüz kartı | `01_DONANIM/SHIELD/` |
| **OPFAIR** | Operfly Air | Hava hızı kartı (pitot fark basınç); sabit kanat için | `01_DONANIM/AIR/` |
| **OPFENG** | Operfly Engine | Benzinli motor izleme ve ateşleme kesme | `01_DONANIM/ENGINE/` |
| **OPFHUB** | Operfly Hub | Omurga anahtar kartı: tüm kartlar buna bağlanır (Gigabit anahtar, CAN FD, güç dağıtımı) | `01_DONANIM/HUB/` |
| **OPFBAS** | Operfly Base | RTK baz istasyonu (yer) | `01_DONANIM/BASE/` |
| **OPFGRD** | Operfly Ground Radio | Yer radyosu | `01_DONANIM/YER_RADYO/` |
| **OPFPCA** | Operfly PC adaptörü | Operfly Bus konnektörü ↔ USB Type-C aktif adaptör | `01_DONANIM/PC_ADAPTOR/` |
| **OPFCEL** | Operfly Cell | 5G kartı: telemetri ve görüntü için hücresel bağlantı | `01_DONANIM/CELL/` |
| **OPFR10 / OPFR30 / OPFR1H** | Operfly Range 10 / 30 / 100 | Mesafe sensörleri: 10 m, 30 m, 100 m | `01_DONANIM/RANGE_10/`, `RANGE_30/`, `RANGE_100/` |
| **OPFRCV** | Operfly RX | Araç tarafı kumanda alıcısı (12 kanal) | `01_DONANIM/RX/` |
| **OPFK12** | Operfly Pilot 12 | Kumanda: yalnızca 12 kanal | `01_DONANIM/KUMANDA_12/` |
| **OPFKTL** | Operfly Pilot T | Kumanda: 12 kanal + telemetri | `01_DONANIM/KUMANDA_T/` |
| **OPFKPR** | Operfly Pilot Pro | Kumanda: 10 inç ekran, yer istasyonu ve video (Jetson) | `01_DONANIM/KUMANDA_PRO/` |
| — | Ortak kart | Kumanda giriş kartı | `01_DONANIM/KUMANDA_GIRIS/` |
| **OPFKMD** | Kumanda yazılımı | Kumandalardaki gömülü yazılım | `02_GOMULU/KUMANDA/` |
| **OPFFLT** | Uçuş yazılımı | Operfly Core üzerinde çalışan otopilot | `02_GOMULU/UCUS/` |
| **OPFNOD** | Düğüm yazılımı | Çevre kartlarındaki Operfly Bus düğümü | `02_GOMULU/DUGUM/` |
| **OPFSEC** | Radyo/kripto yazılımı | Uçtan uca şifreleme, anahtar yönetimi, radyo modülü ayarları | `02_GOMULU/RADYO/` |
| **OPFMRK** | Merkez | Kiracılı çevrimiçi merkez: kurum, filo, cihaz, lisans, güncelleme | `03_MERKEZ/` |
| **OPFGCS** | Yer istasyonu | Çok araçlı görev, izleme ve sürü kontrolü | `04_YER_ISTASYONU/` |
| **OPFIMG** | Görüntü yazılımı | Operfly Vision üzerinde çalışan görüntü işleme | `05_GORUNTU/` |
| **OPFCMP / OPFADM / OPFWEB** | Paneller | Kurum paneli, yönetim paneli, tanıtım sitesi | `06_PANELLER/` |

Bu ürün kodları dosya, klasör, sürüm notu ve teknik iletişimde değişmeden kullanılır.

## Kapsam dışı (dışarıdan alınır)

Batarya, şarj cihazı, motor ve ESC şimdilik dışarıdan satın alınır. Sistem 2S–12S arasındaki hazır
bataryalarla çalışır; kendi bataryası ve şarj cihazı ertelenmiştir.

## Değişmez kurallar

1. **Kapalı ekosistem.** Operfly kartları ve yazılımı yalnızca kimliği doğrulanmış Operfly bileşenleriyle
   konuşur. Üçüncü taraf yer istasyonu yazılımları bağlanamaz.
2. **Marka temizliği.** Üçüncü taraf otopilot, protokol ve yer istasyonu adları kaynak adlarında, arayüzde,
   derlenmiş çıktıda ve cihazın dışarı verdiği hiçbir metinde geçmez. Bu adlar yalnızca
   `13_DOKUMANTASYON/` altında ve üçüncü taraf kaynak dosyalarının korunması zorunlu lisans başlıklarında
   bulunur. Denetim: `10_ORTAK_ARACLAR/marka_denetle.py`.
3. **Kiracı yalıtımı.** Her kurumun cihazları, anahtarları ve verisi diğer kurumlardan ayrıdır.
4. **Sürü önceliği.** Her bileşen çok araçlı kullanım varsayılarak tasarlanır.

Ayrıntı: `13_DOKUMANTASYON/MIMARI.md`.

## Sahiplik

© 2026 Muhammed Kaderoğlu. Tüm hakları saklıdır. Bu depodaki tasarım dosyaları ve yazılım izinsiz
kopyalanamaz, dağıtılamaz veya kullanılamaz.
