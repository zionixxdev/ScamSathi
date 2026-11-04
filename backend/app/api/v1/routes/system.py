"""Health and statistics endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_client_id, get_repository, rate_limit_default
from app.config import get_settings
from app.db.repository import ScanRecord, SqlScanRepository
from app.schemas.analysis import CategoryOut, HealthOut, HistoryItem, StatsOut

router = APIRouter(tags=["system"])

HIGH_RISK = {"High", "Critical"}


def _to_item(record: ScanRecord) -> HistoryItem:
    return HistoryItem(
        scan_id=record.id,
        scan_type=record.scan_type,
        channel=record.channel,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        category=CategoryOut(key=record.category, label=record.category_label),
        confidence=record.confidence,
        excerpt=record.excerpt,
        created_at=record.created_at,
    )


@router.get("/health", response_model=HealthOut, tags=["system"])
def health() -> HealthOut:
    settings = get_settings()
    dialect = settings.database_url.split(":", 1)[0]
    return HealthOut(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        ai_provider=settings.ai_provider if settings.ai_api_key else "none",
        url_reputation_provider=(
            settings.reputation_provider if settings.safebrowsing_api_key else "none"
        ),
        database=dialect,
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/stats", response_model=StatsOut, dependencies=[Depends(rate_limit_default)])
def stats(
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> StatsOut:
    if not client_id:
        return StatsOut(
            total_scans=0,
            high_risk_scans=0,
            by_risk_level={},
            by_category=[],
            recent=[],
            demo_data=False,
            note="No client id was provided, so no stored scans were read. Scans are stored per browser profile only.",
        )
    data = repository.stats(client_id)
    by_level: dict[str, int] = data["by_risk_level"]
    return StatsOut(
        total_scans=data["total_scans"],
        high_risk_scans=sum(count for level, count in by_level.items() if level in HIGH_RISK),
        by_risk_level=by_level,
        by_category=data["by_category"],
        recent=[_to_item(record) for record in data["recent"]],
        demo_data=False,
    )
