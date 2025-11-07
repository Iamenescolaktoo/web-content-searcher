import os, json, datetime, re
from urllib.parse import urlparse
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from services.scraper import fetch_rss_items
from services.analyzer import analyze_text_structured
from services.scoring import compute_risk
from services.alerts import maybe_alert
from storage.db import init_db, save_news_item, fetch_news_for_date
from services.feeds import PRESET_FEEDS

load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

init_db()
scheduler = BackgroundScheduler(daemon=True)

# --- deny rules ---
DENY_HOSTS = {"haberturk.com", "www.haberturk.com"}
DENY_PATH_SUBSTR = {("/aa.com.tr", "/teyithatti")}  # (host_suffix, path_fragment)

def is_blocked_url(url: str) -> bool:
    try:
        p = urlparse(url)
        host = (p.netloc or "").lower()
        path = (p.path or "").lower()
        # block host match
        if host in DENY_HOSTS or any(host.endswith(h.replace("/", "")) for h in DENY_HOSTS):
            return True
        # block aa.com.tr/teyithatti specifically
        if host.endswith("aa.com.tr") and "/teyithatti" in path:
            return True
        return False
    except Exception:
        return False

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("frontend", path)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "time": datetime.datetime.utcnow().isoformat()})

@app.route("/api/presets", methods=["GET"])
def presets():
    return jsonify({"presets": list(PRESET_FEEDS.keys())})

@app.route("/scrape", methods=["GET"])
def scrape():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "missing url"}), 400
    if is_blocked_url(url):
        return jsonify({"error": "scraping not permitted for this source"}), 403
    max_news = int(request.args.get("max_news", os.getenv("DEFAULT_MAX_NEWS", 8)))
    fast = request.args.get("fast", os.getenv("DEFAULT_FAST", "1")) == "1"
    items = fetch_rss_items(url, max_items=max_news, fast=fast)
    return jsonify({"data": items})

@app.route("/metin_analiz", methods=["POST"])
def metin_analiz():
    body = request.get_json(force=True, silent=True) or {}
    text = body.get("metin", "").strip()
    if not text:
        return jsonify({"error": "missing 'metin'"}), 400
    analysis = analyze_text_structured(text)
    return jsonify(analysis)

@app.route("/api/news", methods=["GET"])
def api_news():
    preset = request.args.get("preset")
    url = request.args.get("url")
    max_news = int(request.args.get("max_news", os.getenv("DEFAULT_MAX_NEWS", 8)))
    fast = request.args.get("fast", os.getenv("DEFAULT_FAST", "1")) == "1"

    if preset:
        if preset not in PRESET_FEEDS:
            return jsonify({"error": f"unknown preset '{preset}'"}), 400
        url = PRESET_FEEDS[preset]
    if not url:
        return jsonify({"error": "provide 'preset' or 'url'"}), 400
    if is_blocked_url(url):
        return jsonify({"error": "scraping not permitted for this source"}), 403

    items = fetch_rss_items(url, max_items=max_news, fast=fast)
    enriched = []
    for it in items:
        text = (it.get("content") or it.get("title") or "").strip()
        analysis = analyze_text_structured(text)
        risk_point, rule_hits = compute_risk(text, analysis)
        record = {
            "title": it.get("title"),
            "source": it.get("source"),
            "datetime": it.get("datetime"),
            "category": analysis.get("category"),
            "sentiment": analysis.get("sentiment"),
            "toxicity": analysis.get("toxicity"),
            "keywords": analysis.get("keywords", []),
            "entities": analysis.get("entities", []),
            "risk_point": risk_point,
            "rule_hits": rule_hits,
        }
        save_news_item(record)
        maybe_alert(record)
        enriched.append(record)
    return jsonify({"data": enriched})

def daily_job():
    presets = list(PRESET_FEEDS.keys())
    for p in presets:
        try:
            with app.test_request_context(f"/api/news?preset={p}&max_news=10&fast=1"):
                api_news()
        except Exception as e:
            print("daily_job error:", e)

scheduler.add_job(daily_job, "cron", hour=int(os.getenv("CRON_HOUR", 6)))
scheduler.start()

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    from storage.db import save_user_email
    data = request.get_json(force=True)
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"error": "missing email"}), 400

    created = save_user_email(email)
    if not created:
        return jsonify({"message": "You are already subscribed."})
    return jsonify({"message": "Email registered successfully!"})


if __name__ == "__main__":
    app.run(port=5001, debug=True)

