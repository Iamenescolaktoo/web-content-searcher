---

## Proje

Proje, Türkiye'deki haber sitelerinden günlük olarak alınan haberlerin, **yapay zeka modeli eğitmeden**, dış servislere ait **hazır AI API'leri** aracılığıyla analiz edilmesini, sınıflandırılmasını, önem derecesine göre sıralanmasını ve uygunsuz içeriklerin tespit edilerek **alarm sistemine konu edilmesini** hedefler.

---

## Proje Bileşenleri (Modüller)
1. **Haber Toplama:** Web scraping, RSS, API gibi yöntemlerle haber metinlerinin toplanması                 
2. **Temizlik & Ön İşleme:** HTML temizliği, Türkçe karakter düzeni, gereksiz sembollerin kaldırılması             
3. **AI API Çağrıları:** Dış servisler üzerinden metnin analiz edilmesi: kategori, duygu, toksisite, önem gibi 
4. **Sonuç İşleme:** API çıktılarının iş kurallarına göre işlenmesi ve uyarı üretimi                       
5. **Arayüz:** Sonuçları gösteren filtrelenebilir kullanıcı arayüzü                                  
6. **Alarm Sistemi:** Ön tanımlı eşik değerlerine göre e-posta, log veya API ile uyarı üretimi              

---

## Girdi – İşlem – Çıktı Yapısı
1. **Girdi:** Günlük haber içerikleri (başlık, içerik, yayın tarihi, kaynak)                          
2. **İşlem:** Metinler, API çağrısı ile analiz edilir (kategori, önem, toksisite, anahtar kelime vb.) 
3. **Çıktı:** Sınıflandırılmış ve puanlanmış haberler, uygunsuz içerik uyarıları, raporlar            

---

## Fonksiyonel Gereksinimler
1. Günlük haberlerin otomatik olarak toplanması
2. Haber metinlerinin temizlenip analiz için API’ye gönderilmesi
3. Aşağıdaki işlemlerin hazır API servisleriyle yapılması:
   * **Kategori belirleme**
   * **Duygu analizi (sentiment analysis)**
   * **Toksisite/uygunsuzluk tespiti (hate, violence, sexual content, misinformation)**
   * **Anahtar kelime ve özet çıkarımı**
   * **Varlık tanıma (Named Entity Recognition)**
4. Gelen çıktılara göre önem puanı hesaplama (iş kuralı tabanlı: örn. içinde “deprem”, “terör” varsa +50 puan)
5. Belirli eşik değerleri geçen içerikler için alarm mekanizması tetikleme
6. Tüm analizleri gösteren ve filtrelenebilen web arayüzü sağlama
7. Günlük, haftalık rapor üretimi (Excel/PDF/JSON)

---

## Fonksiyonel Olmayan Gereksinimler
1. **API hız sınırlarına uyum:** Rate limit'e göre çağrılar belirli periyotta gönderilmeli. Kuyruk yapısı da kullanılabilir.                            
2. **Veri gizliliği:** Kişisel veri içeren haberlerde KVKK uyumu, API loglaması anonimleştirilmeli 
3. **Uptime ve Hata Yönetimi:** API kesintilerine karşı retry mekanizması                                   
4. **Geliştirilebilirlik:** Yeni kaynak ekleme veya yeni API bağlama kolay olmalı                       

---

## Riskler ve Önlemler
1. **API'lerin Türkçe destek sınırlılığı:** Gelişmiş destek sunan servisler (Google, OpenAI) tercih edilmeli                                    
2. **Maliyet artışı:** Token bazlı fiyatlandırmaya karşı önbellekleme (cache), sık analiz yapılmayan içeriklerde sınırlama 
3. **Gizlilik ve veri paylaşımı:** Hassas içerikler için anonimleştirme katmanı eklenebilir                                            
4. **API kesintileri / kota dolması:** Failover mekanizması, API servisi değiştirme opsiyonu düşünülmeli                                   

---

## Teknoloji ve Araçlar
1. **Scraper:** Python + Newspaper3k, BeautifulSoup      
2. **API çağrıları:** Python `requests` / `httpx`, async queue 
3. **Veri yönetimi:**  PostgreSQL / SQLite                      
4. **Arayüz:** Flask + React / Streamlit                
5. **Alarm:** SMTP, Slack, Webhook API                 
6. **Raporlama:** Pandas, OpenPyXL, Jinja2 (PDF/Excel)     

---
