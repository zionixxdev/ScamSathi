"""Analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_client_id, get_repository, rate_limit_analyze
from app.db.repository import SqlScanRepository
from app.schemas.analysis import AnalysisResult, MessageAnalysisRequest, UrlAnalysisRequest
from app.services.analysis_service import AnalysisService
from app.services.detection.engine import get_engine

router = APIRouter(prefix="/analyze", tags=["analysis"])


@router.post(
    "/message",
    response_model=AnalysisResult,
    summary="Analyse a message, job offer or payment request",
    dependencies=[Depends(rate_limit_analyze)],
)
async def analyze_message(
    payload: MessageAnalysisRequest,
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> AnalysisResult:
    service = AnalysisService(get_engine(), repository)
    return await service.analyze_message(
        content=payload.content,
        channel=payload.channel.value,
        language=payload.language.value,
        sender_id=payload.sender_id,
        client_id=client_id,
        store=payload.store,
    )


@router.post(
    "/url",
    response_model=AnalysisResult,
    summary="Analyse a URL without opening it",
    dependencies=[Depends(rate_limit_analyze)],
)
async def analyze_url(
    payload: UrlAnalysisRequest,
    client_id: str | None = Depends(get_client_id),
    repository: SqlScanRepository = Depends(get_repository),
) -> AnalysisResult:
    service = AnalysisService(get_engine(), repository)
    return await service.analyze_url(url=payload.url, client_id=client_id, store=payload.store)
