# Üçüncü Taraf Bileşenler ve Lisanslar

Bu dosya, üçüncü taraf adlarının geçtiği tek yerdir. Buradaki bildirimler ürün dokümanında da yer almalıdır.

| Bileşen | Kullanıldığı yer | Lisans | Yükümlülük |
|---|---|---|---|
| PX4 Autopilot | OPFFLT, OPFNOD | BSD 3-Clause | Telif bildirimi ve lisans metni ürün dokümanında; kaynak dosyalardaki lisans başlıkları silinmez |
| Apache NuttX | OPFFLT, OPFNOD | Apache License 2.0 | Lisans metni ve NOTICE dokümanda |
| MAVLink (üretilmiş başlıklar) | Araç içi haberleşme | MIT | Telif bildirimi dokümanda |

Not: Bu tablo hukuki görüş değildir; dağıtım öncesinde bir lisans hukukçusuyla teyit edilmelidir.

## Karar (14 Kasım 2026): lisanslara tam uyum

1. Üçüncü taraf kaynak dosyalarındaki telif ve lisans başlıkları değiştirilmez ve silinmez.
2. Bu kaynak ağaçları `.marka_muaf` dosyasıyla işaretlenir; marka denetimi yalnızca bu klasörleri atlar.
3. Her ürünün kullanıcı dokümanında "Üçüncü taraf lisansları" bölümü bulunur: telif bildirimi,
   lisans koşulları ve sorumluluk reddi tam metin olarak yer alır.
4. Üçüncü taraf proje adları ürünü tanıtmak veya onay ima etmek için kullanılmaz.
5. Derlenmiş yazılımda, arayüzde ve cihazın dışarı verdiği metinlerde yalnızca Operfly adı görünür.
6. Yeni bir üçüncü taraf bileşen eklenmeden önce lisansı bu tabloya işlenir; kaynak açma
   yükümlülüğü getiren (GPL/LGPL/AGPL) bileşenler onay alınmadan eklenmez.
