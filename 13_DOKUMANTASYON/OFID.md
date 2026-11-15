# Operfly Donanım Adresi — OFID (taslak)

Her Operfly kartı, batarya ve kumanda üretimde yazılan, değiştirilemeyen 64 bitlik bir adres taşır.

| Alan | Boyut | İçerik |
|---|---|---|
| Ekosistem öneki | 8 bit | Sabit Operfly işareti |
| Ürün türü | 8 bit | Ürün kodu tablosundan |
| Donanım revizyonu | 8 bit | Revizyon ve varyant |
| Üretim partisi | 8 bit | Üretim yeri ve dönemi |
| Seri numarası | 32 bit | Tür ve parti içinde tekil |

Yazım: sekiz çift onaltılık hane, örn. `0F:02:01:1A:00:00:3C:7E`.

Kurallar:
- Güvenli elemana üretimde bir kez yazılır.
- Adres tek başına kimlik değildir; kart sertifikası adresi içerir ve üretim anahtarıyla imzalıdır.
- Hub port tablosu, düğüm kimliği, kurum/araç kaydı, sürü kimliği, iptal listesi ve servis geçmişi OFID ile tutulur.
- Ethernet MAC adresi OFID'den türetilir; dış ağa çıkan ürünler için IEEE adres bloğu alınır.
- Ürün türü kodlarının tek kaynağı: `02_GOMULU/ORTAK_PROTOKOL/`.
