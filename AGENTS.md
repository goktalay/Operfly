# OPERFLY — Ajan Çalışma Kuralları

İlk olarak `00_BASLANGIC/README.md` ve `13_DOKUMANTASYON/MIMARI.md` dosyalarını okuyun.

## Değişmez sınırlar

- Operfly kapalı bir ekosistemdir; üçüncü taraf yer istasyonu veya kart desteği eklenmez.
- Üçüncü taraf otopilot/protokol/yer istasyonu adları `13_DOKUMANTASYON/` dışında yazılmaz
  (korunması zorunlu lisans başlıkları hariç). Her değişiklikten sonra `marka_denetle.py` çalıştırılır.
- Kiracı yalıtımı her sorguda ve her uçta zorunludur; kiracı kimliği olmayan veri erişimi yazılmaz.
- Sırlar, özel anahtarlar, imza anahtarları, canlı veri ve müşteri verisi depoya eklenmez.

## Mühendislik disiplini

1. Küçük, hedefli ve geri alınabilir değişiklik yapın.
2. Donanım değişikliklerinde KiCad ERC/DRC, yazılım değişikliklerinde derleme ve testleri çalıştırın.
3. Yayın öncesinde SHA-256 ve imza doğrulaması yapın.
