"""Request and response models for the analysis endpoints."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Channel(str, Enum):
    sms = "sms"
    whatsapp = "whatsapp"
    email = "email"
    job_offer = "job_offer"
    payment_request = "payment_request"
    other = "other"


class Language(str, Enum):
    auto = "auto"
    en = "en"
    hi = "hi"
    hinglish = "hinglish"


class MessageAnalysisRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Message text to analyse")
    channel: Channel = Channel.other
    language: Language = Language.auto
    sender_id: str | None = Field(
        default=None,
        max_length=32,
        description="Optional SMS sender id / DLT header, e.g. 'VM-SBIINB'",
    )
    store: bool = Field(default=True, description="Persist a redacted summary in scan history")

    @field_validator("content")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be empty")
        return value


class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048, description="URL to analyse")
    store: bool = True

    @field_validator("url")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("url must not be empty")
        return value.strip()


class CategoryOut(BaseModel):
    key: str
    label: str


class SecondaryCategory(BaseModel):
    key: str
    label: str
    score: int


class IndicatorOut(BaseModel):
    id: str
    label: str
    category: str
    weight: int
    severity: Literal["info", "low", "medium", "high"]
    evidence: str = ""
    explanation: str = ""
    source: Literal["rule", "nlp", "url", "ai"] = "rule"


class MitigatorOut(BaseModel):
    id: str
    label: str
    explanation: str = ""


class UrlFindingOut(BaseModel):
    id: str
    label: str
    weight: int
    evidence: str = ""
    explanation: str = ""


class UrlAnalysisOut(BaseModel):
    submitted: str
    normalized: str
    host: str
    scheme: str
    https: bool
    is_ip_literal: bool
    is_shortener: bool
    is_punycode: bool
    lookalike_of: str | None = None
    risk_score: int
    risk_level: str
    findings: list[UrlFindingOut]
    reputation: "ReputationOut"
    disclaimer: str


class ReputationOut(BaseModel):
    checked: bool
    provider: str | None = None
    verdict: str = "not_checked"
    note: str = "No reputation provider is configured, so the URL was not checked against any external database."


class AiInsightOut(BaseModel):
    used: bool = False
    provider: str | None = None
    rationale: str | None = None
    score_adjustment: int = 0
    note: str | None = None


class AnalysisResult(BaseModel):
    scan_id: str
    scan_type: Literal["message", "url"]
    channel: str = "other"
    created_at: datetime
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High", "Critical", "Uncertain"]
    category: CategoryOut
    secondary_categories: list[SecondaryCategory] = []
    confidence: float = Field(..., ge=0, le=1)
    uncertainty: str | None = None
    language: str = "en"
    indicators: list[IndicatorOut] = []
    mitigators: list[MitigatorOut] = []
    explanation: str
    recommended_actions: list[str] = []
    excerpt: str = ""
    ai: AiInsightOut = AiInsightOut()
    url_analysis: UrlAnalysisOut | None = None
    stored: bool = False
    disclaimer: str = ""


class HistoryItem(BaseModel):
    scan_id: str
    scan_type: str
    channel: str
    risk_score: int
    risk_level: str
    category: CategoryOut
    confidence: float
    excerpt: str
    created_at: datetime


class HistoryPage(BaseModel):
    items: list[HistoryItem]
    total: int
    limit: int
    offset: int


class StatsOut(BaseModel):
    total_scans: int
    high_risk_scans: int
    by_risk_level: dict[str, int]
    by_category: list[dict]
    recent: list[HistoryItem]
    demo_data: bool = False
    note: str = "Counts reflect only the scans stored for this browser profile. No platform-wide figures are shown."


class HealthOut(BaseModel):
    status: str
    version: str
    environment: str
    ai_provider: str
    url_reputation_provider: str
    database: str
    timestamp: datetime


UrlAnalysisOut.model_rebuild()
