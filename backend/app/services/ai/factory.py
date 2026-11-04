"""Provider selection based on configuration."""

from __future__ import annotations

from app.config import get_settings
from app.services.ai.base import AIProvider, NullProvider
from app.services.ai.openai_compatible import OpenAICompatibleProvider


def get_ai_provider() -> AIProvider:
    settings = get_settings()
    if settings.ai_provider in {"openai", "openai_compatible"} and settings.ai_api_key:
        return OpenAICompatibleProvider(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
            model=settings.ai_model,
            timeout=settings.ai_timeout,
        )
    return NullProvider()
