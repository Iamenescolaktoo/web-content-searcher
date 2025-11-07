import os, json, re, requests
from tenacity import retry, stop_after_attempt, wait_exponential

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def _mask_pii(text: str) -> str:
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL]', text)
    text = re.sub(r'(\+?\d[\d\s\-()]{7,}\d)', '[PHONE]', text)
    return text

@retry(stop=stop_after_attempt(4), wait=wait_exponential(multiplier=1, min=1, max=8))
def analyze(text: str) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    masked = _mask_pii(text)
    prompt = (
        "You are a Turkish news analysis API. Return ONLY valid JSON with keys:\n"
        "category (one of: Politics, Economy, Technology, Sports, Health, World, Local, Culture, Crime, Disaster, Other),\n"
        "sentiment (Positive|Neutral|Negative),\n"
        "toxicity (float 0-1),\n"
        "keywords (array of up to 8 lowercase Turkish keywords),\n"
        "entities (array of objects: {text, type}), where type in [PERSON, ORG, LOC, EVENT].\n"
        "Text is in Turkish.\n"
    )
    payload = {
      "model": "gpt-4o-mini",
      "temperature": 0.2,
      "response_format": {"type": "json_object"},
      "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": masked[:6000]}
      ]
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"},
        data=json.dumps(payload),
        timeout=30
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)
    data["toxicity"] = float(max(0.0, min(1.0, data.get("toxicity", 0.0))))
    data["keywords"] = [k.strip().lower() for k in data.get("keywords", [])][:8]
    data["category"] = data.get("category", "Other")
    data["sentiment"] = data.get("sentiment", "Neutral")
    data["entities"] = data.get("entities", [])
    return data
