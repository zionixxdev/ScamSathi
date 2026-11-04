"""Application service that ties the engine to storage.

The service owns the privacy rules: a scan is only persisted when the caller
sent a valid client id and did not opt out, and only a redacted excerpt is kept.
"""

from __future__ import annotations

from app.core.security import content_hash
from app.db.repository import ScanRecord, ScanRepository
from app.schemas.analysis import AnalysisResult
from app.services.detection.engine import DetectionEngine


class AnalysisService:
    def __init__(self, engine: DetectionEngine, repository: ScanRepository | None = None) -> None:
        self._engine = engine
        self._repository = repository

    async def analyze_message(
        self,
        *,
        content: str,
        channel: str,
        language: str,
        sender_id: str | None,
        client_id: str | None,
        store: bool,
    ) -> AnalysisResult:
        result = await self._engine.analyze_message(
            content=content, channel=channel, language=language, sender_id=sender_id
        )
        return self._maybe_store(result, client_id=client_id, store=store, raw=content)

    async def analyze_url(
        self, *, url: str, client_id: str | None, store: bool
    ) -> AnalysisResult:
        result = await self._engine.analyze_url_scan(url=url)
        return self._maybe_store(result, client_id=client_id, store=store, raw=url)

    def _maybe_store(
        self, result: AnalysisResult, *, client_id: str | None, store: bool, raw: str
    ) -> AnalysisResult:
        if not store or not client_id or self._repository is None:
            result.stored = False
            return result
        record = ScanRecord(
            id=result.scan_id,
            client_id=client_id,
            scan_type=result.scan_type,
            channel=result.channel,
            risk_score=result.risk_score,
            risk_level=result.risk_level,
            category=result.category.key,
            category_label=result.category.label,
            confidence=result.confidence,
            excerpt=result.excerpt,
            content_hash=content_hash(raw),
            payload=result.model_dump_json(),
            created_at=result.created_at,
        )
        self._repository.add(record)
        result.stored = True
        return result
