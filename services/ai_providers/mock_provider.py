import re

# minimal Turkish stopwords (extend as needed)
STOP_TR = {
  "ve","veya","ile","de","da","bu","şu","o","bir","iki","üç","dört","beş","çok","az",
  "için","gibi","olarak","ancak","fakat","ama","en","mi","mu","mü","mı","diye","ile",
  "ise","yine","daha","her","hem","ne","nasıl","niçin","neden","ki","ya","ya da","içinde",
  "üzerine","sonra","önce","artık","yerine","var","yok","şimdi","bugün","dün","yarın","biz",
  "siz","onlar","ben","sen","o","birçok","hangi","bazı","ise","bile","kadar","üzere","karşı",
}

# category keyword hints (simple heuristic)
CAT_HINTS = {
  "Disaster": {"deprem","yangın","sel","kasırga","fırtına","çığ","tsunami","enkaz","patlama","uçak","kaza"},
  "Crime": {"cinayet","tutuklama","soygun","yolsuzluk","uyuşturucu","gözaltı","rehine","bomba","saldırı"},
  "Politics": {"bakan","meclis","kabine","cumhurbaşkanı","milletvekili","seçim","kongre","chp","akp","mhp","mevzuat","kanun"},
  "Economy": {"enflasyon","faiz","döviz","kur","banka","bütçe","ekonomi","ihracat","ithalat","piyasa"},
  "Sports": {"futbol","basketbol","voleybol","maç","gol","lig","transfer"},
  "Health": {"sağlık","hastane","doktor","aşı","enfeksiyon","koronavirüs"},
  "World": {"abd","rusya","gazze","israil","avrupa","almanya","fransa","ukrayna","iran","suriye"},
}

NEG_WORDS = {"ölü","yaralı","saldırı","terör","patlama","kriz","skandal","yolsuzluk","cinayet","düştü","açlık"}
POS_WORDS = {"rekor","başarı","artış","iyileşme","destek","barış","kurtarıldı","kazan"}
URL_PAT = re.compile(r'https?://\S+|www\.\S+', re.IGNORECASE)
DOMAIN_PAT = re.compile(r'\b[a-z0-9.-]+\.(com|net|org|tr|gov|edu)(/\S*)?', re.IGNORECASE)
TOKEN_PAT = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]{3,}", re.UNICODE)

def _clean_text(text: str) -> str:
    t = URL_PAT.sub(" ", text or "")
    t = DOMAIN_PAT.sub(" ", t)
    return t

def _tokens(text: str):
    for m in TOKEN_PAT.finditer(text.lower()):
        w = m.group(0)
        if w in STOP_TR: 
            continue
        yield w

def extract_keywords(text: str, top_k: int = 8):
    freq = {}
    for w in _tokens(_clean_text(text)):
        freq[w] = freq.get(w, 0) + 1
    # drop ultra-generic junk that sometimes sneaks in
    bad = {"https","http","trthaberstatic","resimler","haber","son","dakika","video","foto"}
    for b in bad: freq.pop(b, None)
    # sort by frequency then by length (favor informative longer words)
    items = sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))
    return [w for w,_ in items[:top_k]]

def infer_category(text: str) -> str:
    low = (_clean_text(text) or "").lower()
    best_cat, best_hits = "Other", 0
    for cat, words in CAT_HINTS.items():
        hits = sum(1 for w in words if w in low)
        if hits > best_hits:
            best_cat, best_hits = cat, hits
    return best_cat if best_hits else "Other"

def infer_sentiment(text: str) -> str:
    low = (_clean_text(text) or "").lower()
    neg = any(w in low for w in NEG_WORDS)
    pos = any(w in low for w in POS_WORDS)
    if neg and not pos: return "Negative"
    if pos and not neg: return "Positive"
    return "Neutral"

def infer_toxicity(text: str) -> float:
    low = (_clean_text(text) or "").lower()
    base = 0.05
    bumps = 0.0
    for w in ["terör","saldırı","bomba","nefret","hakaret","ölü","cinayet","soykırım","şiddet"]:
        if w in low: bumps += 0.15
    return float(max(0.0, min(1.0, base + bumps)))

def analyze(text: str) -> dict:
    kw = extract_keywords(text or "")
    return {
        "category": infer_category(text or ""),
        "sentiment": infer_sentiment(text or ""),
        "toxicity": round(infer_toxicity(text or ""), 2),
        "keywords": kw,
        "entities": []  # mock provider doesn’t do NER
    }
