# Otomatik Tanıma ve Görsel Kurulum (taslak)

Hub'a bir kart takıldığında yer istasyonu onu aracın canlı şemasında gösterir ve gereken ayarı
görsel bir sihirbazla yaptırır.

1. **Algılama:** Hub port numarasını ve akımı bildirir; kart sertifikasıyla doğrulanır.
2. **Kendini tanıtma:** Her kart bir tanım belgesi taşır (tür, sürüm, parametreler, sınırlar, kurulum soruları).
3. **Şema:** Araç, Hub merkezli çizilir: port, kart, bağlantı durumu, tüketim, sağlık.
4. **Görsel kurulum:** Yeni kart için sihirbaz (ör. Range bakış yönü, Nav anten konumu, kamera rolü).
5. **Doğrulama:** Çakışma, eksik rol ve güç bütçesi denetimi.
6. **Saklama:** Ayar kartta ve araç kaydında; merkezde kurum bazında yedek.

Kurallar:
- Yer istasyonunda kart türüne özel kod yazılmaz; ekranlar tanım belgesinden üretilir.
- Tanım belgesinin biçimi `02_GOMULU/ORTAK_PROTOKOL/` altında tek kaynak olarak tutulur.
- Uçuşu etkileyen ayarlar yalnızca yerde değiştirilebilir.

Açık konular: tanım belgesi biçimi, şema çizim kuralları, araç gövde çizimlerinin kaynağı.
