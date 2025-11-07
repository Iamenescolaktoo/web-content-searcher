import os
from services.ai_providers import mock_provider

PROVIDER = os.getenv("PROVIDER", "mock").lower()

def analyze_text_structured(text: str) -> dict:
    if PROVIDER == "openai":
        from services.ai_providers import openai_provider
        try:
            return openai_provider.analyze(text)
        except Exception:
            return mock_provider.analyze(text)
    return mock_provider.analyze(text)
