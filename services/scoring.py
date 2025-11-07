 # Rule-based risk scoring
CRITICAL_TERMS = [
    ("deprem", 50), ("terör", 50), ("patlama", 35), ("saldırı", 35),
    ("intihar", 30), ("cinayet", 30), ("şiddet", 20), ("yolsuzluk", 20),
    ("tsunami", 40), ("sel", 25), ("yangın", 25), ("bomba", 40), ("rehine", 40),
]

CATEGORY_WEIGHTS = {"Disaster": 20, "Crime": 15, "Politics": 5}
SENTIMENT_WEIGHTS = {"Negative": 5, "Neutral": 0, "Positive": -3}

def compute_risk(text: str, analysis: dict) -> tuple[int, list]:
    score, hits = 0, []
    low = (text or "").lower()
    for term, w in CRITICAL_TERMS:
        if term in low:
            score += w; hits.append(f"term:{term}+{w}")
    cat = analysis.get("category")
    if CATEGORY_WEIGHTS.get(cat):
        score += CATEGORY_WEIGHTS[cat]; hits.append(f"category:{cat}+{CATEGORY_WEIGHTS[cat]}")
    tox = float(analysis.get("toxicity", 0.0)); tox_pts = int(round(tox * 10))
    score += tox_pts
    if tox_pts: hits.append(f"toxicity:{tox}->{tox_pts}")
    sent = analysis.get("sentiment"); s_pts = SENTIMENT_WEIGHTS.get(sent, 0)
    score += s_pts
    if s_pts: hits.append(f"sentiment:{sent}+{s_pts}")
    ui_score = max(0, min(10, score // 10))
    return ui_score, hits
