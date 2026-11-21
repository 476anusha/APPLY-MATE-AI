"""Factory for obtaining the active AIProvider instance."""
import logging
import os
from typing import Optional

from .base import AIProvider
from .gemini_provider import GeminiProvider
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

# Cached provider singleton
_provider_instance: Optional[AIProvider] = None


def get_ai_provider(force_refresh: bool = False) -> AIProvider:
    """Return the configured AI provider.

    Priority:
    1. GeminiProvider if GEMINI_API_KEY is configured
    2. OpenAIProvider if OPENAI_API_KEY is configured
    3. MockProvider (Demo mode / fallback)
    """
    global _provider_instance

    if _provider_instance is not None and not force_refresh:
        return _provider_instance

    # Safely inspect settings or environment variables
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    try:
        from app.core.config import settings
        if getattr(settings, "GEMINI_API_KEY", None):
            gemini_key = settings.GEMINI_API_KEY
        if getattr(settings, "OPENAI_API_KEY", None):
            openai_key = settings.OPENAI_API_KEY
    except Exception:
        # Settings might still be loading or config module not yet instantiated
        pass

    # Ignore placeholder values
    if gemini_key and "your-gemini-api-key" not in gemini_key.lower():
        logger.info("Initializing GeminiProvider as primary AI provider")
        _provider_instance = GeminiProvider(api_key=gemini_key)
    elif openai_key and "your-openai-api-key" not in openai_key.lower():
        logger.info("Initializing OpenAIProvider as primary AI provider")
        _provider_instance = OpenAIProvider(api_key=openai_key)
    else:
        logger.info("No AI API keys configured; utilizing MockProvider in Demo mode")
        _provider_instance = MockProvider()

    return _provider_instance
