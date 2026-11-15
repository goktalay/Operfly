# Operfly Mimarisi (taslak)

## Katmanlar

1. **Donanım:** Core, Hub, Power, Nav, Radio, RX, Vision ve diğer kartlar (liste: README); Operfly Bus (güç + CAN FD + Ethernet).
2. **Gömülü:** uçuş yazılımı (OPFFLT), düğüm yazılımı (OPFNOD), radyo/kripto yazılımı (OPFSEC).
3. **Merkez (OPFMRK):** kiracılı çevrimiçi merkez.
4. **Yer istasyonu (OPFGCS)** ve paneller.

## Kiracı modeli

Kurum (kiracı) → Filo → Araç → Kart.

- Her kart üretimde güvenli elemanına yazılan bir cihaz sertifikası taşır; sertifika kartı bir kuruma bağlar.
- Kart, yalnızca kendi kurumunun sertifika zincirini taşıyan kartlarla ve yer istasyonuyla oturum açar.
- Merkez; kurum, kullanıcı, rol, filo, araç, kart, lisans ve yazılım sürümlerini kurum bazında tutar.
- Yer istasyonu çevrimdışı çalışabilir; kurum sertifikası ve lisans belgesi yerelde doğrulanır.

## Kapalı ekosistem

- Kart dışına çıkan her bağlantı (RF, Ethernet, USB) karşılıklı kimlik doğrulama ve şifreleme ister.
- Araç içi protokol dışarıya hiçbir arayüzden ham olarak verilmez; dış arayüz yalnızca Operfly protokolüdür.
- Üretim yazılımında USB ve seri servis portları kilitlidir; servis erişimi imzalı servis belgesiyle açılır.
- Yazılım güncellemeleri imzalıdır; kart imzasız veya başka kuruma ait paketi reddeder.

## Sürü

Araç kimliği sertifikadan gelir; radyo ağı mesh ve frekans atlamalıdır; çift bazlı oturum anahtarı ve
grup anahtarı kullanılır; ele geçen araç merkezden iptal edilir.

## Açık kararlar

Radyo modülü seçimi, Operfly Bus konnektörü, Operfly protokolünün tel biçimi, hedef standart listesi.
