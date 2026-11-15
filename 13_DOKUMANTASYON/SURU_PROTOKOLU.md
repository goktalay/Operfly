# Sürü İçi Çarpışma Önleme Protokolü (taslak)

Araçlar yer istasyonuna bağlı olmadan birbirleriyle doğrudan konuşur; çarpışma araç üzerinde önlenir.

| Katman | Tasarım |
|---|---|
| Durum yayını | Konum, hız, belirsizlik ve kısa vadeli niyet; saniyede en az 10 kez, mesh ağa |
| Zaman | Operfly Nav zaman damgası; eski mesaj ileriye doğru tahmin edilir |
| Karar | Komşu rotalarıyla karşılaştırma; çakışmada karşılıklı hız engeli yöntemiyle kaçınma hızı |
| Kural | Sabit geçiş kuralları ve araç kimliğine dayalı öncelik |
| Güvenlik payı | Ayrım mesafesi konum belirsizliğiyle büyür |
| Bağlantı kaybı | Son bilinen rota varsayılır, pay artırılır, gerekirse irtifa katmanına ayrılır |
| Doğrulama | Mesajlar grup anahtarıyla imzalanır; yabancı yayın dikkate alınmaz |
| GNSS'siz yedek | Opsiyonel araçlar arası mesafe ölçümü (UWB) ve Operfly Range verisi |

Açık konular: tel biçimi, yayın hızı/bant genişliği bütçesi, kaçınma parametreleri, simülasyon senaryoları.
Kural: simülasyonla doğrulanmadan uçuşa alınmaz.
