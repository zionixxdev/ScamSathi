"""Environment driven configuration.

Only the standard library plus python-dotenv is used so that the service can
boot in constrained environments (free tier hosts, CI) without extra setup.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

try:  # pragma: no cover - optional convenience dependency
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except Exception:  # pragma: no cover
    pass


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip() or default)
    except ValueError:
        return default


def _rate(name: str, default: str) -> tuple[int, int]:
    raw = (os.getenv(name) or default).strip()
    try:
        requests, window = raw.split("/", 1)
        return max(1, int(requests)), max(1, int(window))
    except Exception:
        requests, window = default.split("/", 1)
        return int(requests), int(window)


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "ScamSathi API"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))

    allowed_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
            ).split(",")
            if origin.strip()
        )
    )

    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./scamsathi.db")
    )

    max_message_chars: int = field(default_factory=lambda: _int("MAX_MESSAGE_CHARS", 5000))
    max_url_chars: int = field(default_factory=lambda: _int("MAX_URL_CHARS", 2048))

    ai_provider: str = field(default_factory=lambda: os.getenv("AI_PROVIDER", "none").strip().lower())
    ai_api_key: str = field(default_factory=lambda: os.getenv("AI_API_KEY", "").strip())
    ai_base_url: str = field(
        default_factory=lambda: os.getenv("AI_BASE_URL", "https://api.openai.com/v1").strip()
    )
    ai_model: str = field(default_factory=lambda: os.getenv("AI_MODEL", "gpt-4o-mini").strip())
    ai_timeout: float = field(default_factory=lambda: float(_int("AI_TIMEOUT_SECONDS", 8)))

    reputation_provider: str = field(
        default_factory=lambda: os.getenv("URL_REPUTATION_PROVIDER", "none").strip().lower()
    )
    safebrowsing_api_key: str = field(
        default_factory=lambda: os.getenv("SAFEBROWSING_API_KEY", "").strip()
    )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def analyze_rate_limit() -> tuple[int, int]:
    return _rate("RATE_LIMIT_ANALYZE", "30/60")


def default_rate_limit() -> tuple[int, int]:
    return _rate("RATE_LIMIT_DEFAULT", "120/60")
