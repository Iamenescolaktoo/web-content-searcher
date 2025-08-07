import traceback
import logging
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ==== CONFIG ====
API_URL = "http://10.150.42.229:11434/api/generate"  # LLM API adresiniz
MODEL = "gemma3:12b"
STREAM = False

# ==== Logging ====
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="LLM API Service", version="2.0")

# ==== CORS ====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== Request & Response Models ====
class AnalizRequest(BaseModel):
    metin: str
    eksik_alanlar: list[str]

class AppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def handle_exceptions(e):
    if isinstance(e, AppException):
        logging.error(f"Tespit edilen hata: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    else:
        logging.error("Hata detayları:\n" + traceback.format_exc())
        raise HTTPException(status_code=500, detail="İşlem sırasında hata oluştu.")

# ==== Prompt Builder ====
def build_prompt(text: str, eksik_alanlar: list[str]):
    return f"""
Aşağıdaki metni analiz et vu şu JSON formatını doldur:
{{"category":"","summary":"","key_emotions":[],"risk_point":0,"keywords":[],"tehlikeAciklama":""}}
Kurallar:
- Sadece eksik olan alanları doldur (eksik alanlar: {eksik_alanlar})
- summary: Metni tek cümlede özetle
- key_emotions: Metindeki baskın duygular (liste)
- risk_point: Toplum için anlık risk puanı(1-10)
- keywords: Metinden çıkarılan en fazla 5 anahtar kelime
- tehlikeAciklama: Metnin tehlike boyutuna dair kısa açıklama
Metin: "{text}"
"""

@app.post("/metin_analiz")
def tehlikeliMetinAnalizEt(request: AnalizRequest):
    try:
        prompt = build_prompt(request.metin, request.eksik_alanlar)
        payload = {"model": MODEL, "prompt": prompt, "stream": STREAM}

        response = requests.post(API_URL, json=payload, timeout=180)
        response.raise_for_status()

        data = response.json()
        llm_response = data.get("response", "").strip()

        # JSON temizleme
        cleaned_response = (
            llm_response.replace("```json", "")
                        .replace("```", "")
                        .strip()
        )

        parsed = json.loads(cleaned_response)
        return parsed
    except Exception as e:
        handle_exceptions(e)

@app.get("/")
def root():
    return {"message": "LLM API - /docs üzerinden Swagger UI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)