from fastapi import FastAPI, Query
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import os
from urllib.parse import urlparse
from typing import Optional

app = FastAPI(title="Genel Haber Scraper API", version="1.1.0")

# --- Genel haber metni çekme fonksiyonu ---
def haber_metnini_getir(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Yaygın haber sitelerinde kullanılan seçiciler
        selector_list = [
            "div.article-content p",
            "div.content-body p",
            "div.news-content p",
            "div.detail-content p",
            "div#newsDetailContent p",
            "div.post-content p",
            "div.entry-content p",
            "article p"
        ]

        metin = ""
        for selector in selector_list:
            paragraflar = soup.select(selector)
            if paragraflar:
                metin = " ".join(p.get_text(strip=True) for p in paragraflar if p.get_text(strip=True))
                break

        # Fallback: hiçbir seçici uymadıysa tüm <p> etiketlerini al
        if not metin:
            fallback = soup.find_all("p")
            metin = " ".join(p.get_text(strip=True) for p in fallback if p.get_text(strip=True))

        return metin.strip() if metin else None
    except Exception as e:
        print(f"Haber metni çekilemedi: {e}")
        return None

# --- RSS'ten haber listesi çek ---
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

            # Görsel galeri/video haberlerini atla
            if any(sub in link for sub in ["galeri", "video", "fotogaleri", "infografik"]):
                continue

            metin = haber_metnini_getir(link)
            if not metin:
                continue

            # Domain adını ID olarak kullan
            parsed_url = urlparse(link)
            host = parsed_url.netloc
            if host.startswith("www."):
                host = host[4:]
            site_adi = host.split('.')[0]

            haber_id = f"{site_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            haberler.append({
                "id": haber_id,
                "source": link,
                "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "title": baslik,
                "text": metin,
                "category": None,
                "summary": None,
                "key_emotions": None,
                "risk_point": None,
                "keywords": None
            })
            time.sleep(1)  # siteyi yormamak için küçük gecikme

        return haberler
    except Exception as e:
        print(f"Hata: {e}")
        return []

# --- Request modeli ---
class ScrapeRequest(BaseModel):
    url: str
    max_news: Optional[int] = 5

@app.get("/")
def root():
    return {"message": "Genel Haber Scraper API çalışıyor! /scrape endpointini kullanın."}

@app.post("/scrape")
def scrape(request: ScrapeRequest):
    haberler = rss_haberleri_cek(request.url, max_haber=request.max_news)
    file_name = f"haberler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(haberler, f, indent=2, ensure_ascii=False)
    return {"count": len(haberler), "data": haberler}

@app.get("/scrape")
def scrape_get(url: str = Query(...), max_news: int = 5):
    haberler = rss_haberleri_cek(url, max_haber=max_news)
    file_name = f"haberler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(haberler, f, indent=2, ensure_ascii=False)
    return {"count": len(haberler), "data": haberler}
