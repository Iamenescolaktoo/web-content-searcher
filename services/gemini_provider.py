import os
import google.generativeai as genai

# Configure Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=AIzaSyB9cK43uI1f_QbS2HA-RnTZz3GlY0oacCI)

MODEL = "gemini-1.5-flash"

DEFAULT_SCHEMA = {
    "sentiment": "Neutral",
    "toxicity": 0.0,
    "category": "General",
    "keywords": [],
    "entities": [],
    "risk_flags": []
}

def analyze(text: str) -> dict:
    try:
        model = genai.GenerativeModel(MODEL)

        prompt = f"""
        Analyze the following news text and respond ONLY in JSON following this schema:

        {{
            "sentiment": "Positive/Neutral/Negative",
            "toxicity": float,
            "category": "string",
            "keywords": ["list"],
            "entities": ["list"],
            "risk_flags": ["list"]
        }}

        Text:
        {text}
        """

        response = model.generate_content(prompt)
        cleaned = response.text.strip()

        # Try parsing JSON
        import json
        try:
            data = json.loads(cleaned)
        except Exception:
            return DEFAULT_SCHEMA

        # Fill missing fields with defaults
        for k, v in DEFAULT_SCHEMA.items():
            if k not in data:
                data[k] = v

        return data

    except Exception as e:
        print("[Analyzer] Gemini provider failed:", e)
        return DEFAULT_SCHEMA
