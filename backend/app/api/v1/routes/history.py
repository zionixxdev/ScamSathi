"""Scan history endpoints.

History is keyed to the anonymous client id sent in the X-Client-Id header, so
one browser can never read another browser's scans.  Deleting a record removes
it permanently.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_client_id, get_repository, rate_limit_default
from app.core.errors import NotFoundError
from app.db.repository import ScanRecord, SqlScanRepository
from app.schemas.analysis import CategoryOut, HistoryItem, HistoryPage

router = APIRouter(prefix="/history", tags=["history"])

RISK_LEVELS = {"Low", "Medium", "High", "Critical", "Uncertain"}


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


@router.get("", response_model=HistoryPage, dependencies=[Depends(rate_limit_default)])
def list_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    risk_level: str | None = Query(default=None),
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> HistoryPage:
    if risk_level and risk_level not in RISK_LEVELS:
        raise NotFoundError("Unknown risk level filter.", code="invalid_filter")
    if not client_id:
        return HistoryPage(items=[], total=0, limit=limit, offset=offset)
    records = repository.list(client_id=client_id, limit=limit, offset=offset, risk_level=risk_level)
    return HistoryPage(
        items=[_to_item(record) for record in records],
        total=repository.count(client_id),
        limit=limit,
        offset=offset,
    )


@router.get("/{scan_id}", dependencies=[Depends(rate_limit_default)])
def get_scan(
    scan_id: str,
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> dict:
    if not client_id:
        raise NotFoundError("This scan is not available without a client id.")
    record = repository.get(scan_id, client_id)
    if record is None:
        raise NotFoundError("Scan not found.")
    import json

    return json.loads(record.payload)


@router.delete(
    "/{scan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(rate_limit_default)],
)
def delete_scan(
    scan_id: str,
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> Response:
    if not client_id or not repository.delete(scan_id, client_id):
        raise NotFoundError("Scan not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
