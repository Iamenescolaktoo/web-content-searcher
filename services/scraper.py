import datetime, ssl
import feedparser
from newspaper import Article

def _safe_now_iso():
    return datetime.datetime.now().isoformat()

def fetch_rss_items(url: str, max_items=8, fast=True):
    ssl._create_default_https_context = ssl._create_unverified_context
    feed = feedparser.parse(url)
    out = []
    for entry in feed.entries[:max_items]:
        item = {
            "title": getattr(entry, "title", "").strip(),
            "source": getattr(entry, "link", ""),
            "datetime": getattr(entry, "published", _safe_now_iso()),
            "content": getattr(entry, "summary", "").strip()
        }
        if not fast and item["source"]:
            try:
                art = Article(item["source"])
                art.download(); art.parse()
                if art.text:
                    item["content"] = art.text.strip()
            except Exception:
                pass
        out.append(item)
    return out
