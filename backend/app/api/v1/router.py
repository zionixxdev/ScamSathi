"""Version 1 API router."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import analyze, history, system

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analyze.router)
api_router.include_router(history.router)
api_router.include_router(system.router)
