import os
from services.ai_providers import mock_provider

PROVIDER = os.getenv("PROVIDER", "mock").lower()

def analyze_text_structured(text: str) -> dict:
    # Use Google Gemini
    if PROVIDER == "gemini":
        try:
            from services.ai_providers import gemini_provider
            return gemini_provider.analyze(text)
        except Exception as e:
            print("[Analyzer] Falling back to mock provider:", e)
            return mock_provider.analyze(text)

    # Use OpenAI (if you switch back in the future)
    if PROVIDER == "openai":
        try:
            from services.ai_providers import openai_provider
            return openai_provider.analyze(text)
        except Exception as e:
            print("[Analyzer] Falling back to mock provider:", e)
            return mock_provider.analyze(text)

    # Default
    return mock_provider.analyze(text)
