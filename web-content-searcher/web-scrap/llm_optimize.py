from pymongo import MongoClient
import requests
import time
from datetime import datetime,timezone
from transformers import pipeline,AutoTokenizer,AutoModelForSeq2SeqLM
from concurrent.futures import ThreadPoolExecutor, as_completed
import torch

tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")



def summarize_text(text, max_length=120, min_length=30):
    # Tokenizer ile encode et ve truncate uygula
    inputs = tokenizer(
        text,
        return_tensors="pt",
        max_length=1024,    # modelin max input length
        truncation=True     # fazlasını kes
    )
    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=4,
        length_penalty=2.0,
        max_length=max_length,
        min_length=min_length,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# ==== CONFIG ====
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "myDatabase"
COLLECTION_NAME = "news"
API_URL = "http://localhost:5000/metin_analiz"  # FastAPI endpointiniz

# ==== Log ====
def log_llm_status(db, doc_id, status, error_message=None):
    db["llm_logs"].insert_one({
        "doc_id": str(doc_id),
        "status": status,
        "error": error_message,
        "timestamp": datetime.now(timezone.utc)
    })

def find_missing_fields(doc):
    eksikler = []
    if doc.get("category") in (None,""): 
        eksikler.append("category")
    if doc.get("summary") in (None,""): 
        eksikler.append("summary")
    if not doc.get("key_emotions"): 
        eksikler.append("key_emotions")
    if doc.get("risk_point") in (None,""): 
        eksikler.append("risk_point")
    if not doc.get("keywords"): 
        eksikler.append("keywords")
    if doc.get("tehlikeAciklama") in (None,""): 
        eksikler.append("tehlikeAciklama")
    return eksikler

def call_analysis_api(text, eksik_alanlar):
    payload = {"metin": text, "eksik_alanlar": eksik_alanlar}
    response = requests.post(API_URL, json=payload, timeout=180)
    response.raise_for_status()
    return response.json()

def process_document(doc, collection, db):
    start_time = time.perf_counter() # timer başlangıç

    doc_id = doc["_id"]
    text = doc.get("text","").strip()

    # Uzun metinleri özetle
    if len(text.split()) > 150:
        text = summarize_text(text)
    
    if not text:
        log_llm_status(db, doc_id,"fail","Boş Metin")
        return
    
    eksik_alanlar = find_missing_fields(doc)
    if not eksik_alanlar:
        return
    
    print(f"İşleniyor: {doc_id} --> Eksikler: {eksik_alanlar}")
    try:
        result = call_analysis_api(text,eksik_alanlar)
        update_fields = {k: v for k, v in result.items() if k in eksik_alanlar}
        if update_fields:
            collection.update_one({"_id": doc_id}, {"$set": update_fields})
            log_llm_status(db, doc_id, "success")
            print(f"Güncellendi: {doc_id}")
        else:
            log_llm_status(db, doc_id, "fail", "API boş döndü")
    except Exception as e:
        print(f"Hata: {doc_id} - {e}")
        log_llm_status(db, doc_id, "fail", str(e))
    
    end_time = time.perf_counter()
    print(f"{doc_id} için süre: {end_time-start_time:.2f} saniye")

def enrich_mongodb():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    query = {
        "$or": [
            {"category": {"$in": [None, ""]}},
            {"summary": {"$in": [None, ""]}},
            {"key_emotions": {"$in": [None, []]}},
            {"risk_point": {"$in": [None, ""]}},
            {"keywords": {"$in": [None, []]}},
            {"tehlikeAciklama": {"$in": [None, ""]}}
        ]
    }
    total_count = collection.count_documents({})
    missing_count = collection.count_documents(query)
    print(f"Toplam veri sayısı: {total_count}")
    print(f"İşlenmesi gereken veri sayısı: {missing_count}")
    documents = list(collection.find(query))

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_document, doc, collection, db) for doc in documents]
        for future in as_completed(futures):
            _ = future.result()
    

if __name__ == "__main__":
    enrich_mongodb()