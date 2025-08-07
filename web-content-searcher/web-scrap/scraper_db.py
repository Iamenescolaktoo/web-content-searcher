# Gerekli kütüphaneler içe aktarılıyor
from fastapi import FastAPI, Query  # API tanımı ve query parametreleri için
from pydantic import BaseModel  # Request gövdesi doğrulama için model tanımı
import requests  # HTTP istekleri göndermek için
from bs4 import BeautifulSoup  # HTML içeriği ayrıştırmak için
from datetime import datetime  # Zaman damgaları için
import time  # Zaman gecikmesi eklemek için
import json, os  # JSON işlemleri ve dosya işlemleri için
from urllib.parse import urlparse  # URL parçalamak için
from typing import Optional  # Opsiyonel tipler tanımlamak için
from pymongo import MongoClient  # MongoDB bağlantısı için
import bson  # ObjectId dönüştürmek için
import feedparser  # RSS beslemelerini analiz etmek için (not: kullanılmıyor)

# MongoDB veritabanına bağlantı kuruluyor
client = MongoClient("mongodb://localhost:27017/")
db = client["myDatabase"]
collection = db["news"]  # Haberlerin kaydedileceği koleksiyon
log_collection = db["logs"]  # İşlem günlükleri için ayrı koleksiyon

# FastAPI uygulaması başlatılıyor
app = FastAPI(title="Genel Haber Scraper API", version="1.1.0")

# ObjectId nesnelerini JSON stringe çevirmek için özel serializer
def bson_serializer(obj):
    if isinstance(obj, bson.ObjectId):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

# Her scrape işlemine dair log verisi kaydediliyor
def log_kaydet(site_adi, url, haber_sayisi):
    log_doc = {
        "site": site_adi,
        "rss_url": url,
        "timestamp": datetime.now().isoformat(),
        "news_count": haber_sayisi
    }
    log_collection.insert_one(log_doc)

# Aynı haber daha önce kaydedilmiş mi kontrolü
def isUnique(link):
    return collection.find_one({"source": link}) is not None

# Haber sayfasından metni çekmek için fonksiyon
def haber_metnini_getir(url):
    headers = {"User-Agent": "Mozilla/5.0"}  # Bot algısını engellemek için
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Farklı sitelerden haber içeriğini bulmak için CSS seçiciler
        selector_list = [
            "div.article-content p", "div.content-body p", "div.news-content p",
            "div.detail-content p", "div#newsDetailContent p", "div.post-content p",
            "div.entry-content p", "article p"
        ]

        metin = ""
        for selector in selector_list:
            paragraflar = soup.select(selector)
            if paragraflar:
                metin = " ".join(p.get_text(strip=True) for p in paragraflar if p.get_text(strip=True))
                break

        # Eğer seçiciler başarısızsa tüm <p> etiketlerinden veri çekilir
        if not metin:
            fallback = soup.find_all("p")
            metin = " ".join(p.get_text(strip=True) for p in fallback if p.get_text(strip=True))

        return metin.strip() if metin else None
    except Exception as e:
        print(f"Haber metni çekilemedi: {e}")
        return None

# RSS URL üzerinden haberleri çekme işlemi
def rss_haberleri_cek(rss_url, max_haber=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")

        haberler = []
        for item in items[:max_haber]:
            baslik = item.title.text.strip()
            link = item.link.text.strip()

            # Galeri, video vb. içerikleri ayıklamak için filtre
            if any(sub in link for sub in ["galeri", "video", "fotogaleri", "infografik"]):
                continue

            if isUnique(link):
                continue  # Aynı haber varsa geç

            metin = haber_metnini_getir(link)
            if not metin:
                continue  # Metin alınamazsa geç

            # Site adı çıkarılıyor
            parsed_url = urlparse(link)
            host = parsed_url.netloc
            if host.startswith("www."):
                host = host[4:]
            site_adi = host.split('.')[0]

            # Haber ID oluşturuluyor
            haber_id = f"{site_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Haber verisi listeye ekleniyor
            haberler.append({
                "news_id": haber_id,
                "source": link,
                "datetime": datetime.now().isoformat(),
                "title": baslik,
                "text": metin,
                "category": None,
                "summary": None,
                "key_emotions": None,
                "risk_point": None,
                "keywords": None
            })
            time.sleep(1)  # Yoğunluk azaltmak için küçük bekleme

        return haberler
    except Exception as e:
        print(f"Hata: {e}")
        return []

# API'ye gelen veri modeli tanımı
class ScrapeRequest(BaseModel):
    url: str
    max_news: Optional[int] = 5

# API'nin ana sayfa endpoint'i
@app.get("/")
def root():
    return {"message": "Genel Haber Scraper API çalışıyor! /scrape endpointini kullanın."}

# POST ile haberleri çekip kaydeden endpoint
@app.post("/scrape")
def scrape(request: ScrapeRequest):
    haberler = rss_haberleri_cek(request.url, max_haber=request.max_news)
    if haberler:
        result = collection.insert_many(haberler)

        parsed_url = urlparse(request.url)
        host = parsed_url.netloc
        if host.startswith("www."):
            host = host[4:]
        site_adi = host.split('.')[0]

        log_kaydet(site_adi, request.url, len(haberler))

        # MongoDB ObjectId'leri stringe çevriliyor
        for i, obj_id in enumerate(result.inserted_ids):
            haberler[i]["_id"] = str(obj_id)

    return {"count": len(haberler), "data": haberler}

# GET methoduyla haber çekip kaydeden endpoint (query parametreli)
@app.get("/scrape")
def scrape_get(url: str = Query(...), max_news: int = 5):
    haberler = rss_haberleri_cek(url, max_haber=max_news)
    if haberler:
        result = collection.insert_many(haberler)

        parsed_url = urlparse(url)
        host = parsed_url.netloc
        if host.startswith("www."):
            host = host[4:]
        site_adi = host.split('.')[0]

        log_kaydet(site_adi, url, len(haberler))

        # ObjectId'leri stringleştirme
        for i, obj_id in enumerate(result.inserted_ids):
            haberler[i]["_id"] = str(obj_id)
        
    return {"count": len(haberler), "data": haberler}
