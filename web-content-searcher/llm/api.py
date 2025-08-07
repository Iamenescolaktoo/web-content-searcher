import traceback
import logging
import base64
import json
import requests
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

API_URL = "http://10.150.42.229:11434/api/generate"
MODEL = "gemma3:12b"
STREAM = False

TXT_DETECTION_PROMPT = """Tırnak içindeki metin şu konulardan birini metaforik olarak da olsa içeriyorsa tehlike puanını yüksek tut. Konu: Terör, provakasyon, tehdit, üstü kapalı tehdit, şiddet.
Cevabı json formatında oluştur. 
Aşağıdaki bilgileri içeren bir JSON formatında cevap ver:
- Metnin içeriğimin tehlike puanı (0 ve 10 dahil olmak üzere bunlar arasında bir değer olmalıdır.)
- İçeriğin tehlike açıklaması (en fazla 300 karakterli kısa bir açıklama olmalıdır.)
JSON yapısı şu şekilde olmalıdır:
{
  "tehlikePuani": 4,
  "tehlikeAciklama": "Metinde şiddet ibareleri var"
}
'{{TXT}}'
"""

# Logging yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="LLM API Service", version="1.0")

# CORS izinleri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class TehlikeTespitResponse(BaseModel):
    tehlikePuani: int
    tehlikeAciklama: str

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

@app.post("/metin_analiz", response_model = TehlikeTespitResponse)
def tehlikeliMetinAnalizEt(metin: str):
    try:
        prompt = TXT_DETECTION_PROMPT.replace("{{TXT}}", metin)
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": STREAM
        }

        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        llm_response = data.get("response", "").strip()
        cleaned_response = llm_response.replace("json", "").replace("\n", "").replace("`", "").strip()
        parsed = json.loads(cleaned_response)
        return TehlikeTespitResponse(**parsed)
    except Exception as e:
        handle_exceptions(e)
        

@app.post("/message_to_llm", response_model = str)
def sendMessageToLLM(request: PromptRequest):
    try:
        payload = {
            "model": MODEL,
            "prompt": request.prompt,
            "stream": STREAM
        }
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        handle_exceptions(e)


@app.get("/")
def root():
    return {"message": "LLM API - Swagger Documentation Available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
