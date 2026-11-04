"""FastAPI dependencies: client identity, repository, rate limiting."""

from __future__ import annotations

from fastapi import Depends, Header, Request
from sqlalchemy.orm import Session

from app.config import analyze_rate_limit, default_rate_limit
from app.core.errors import RateLimitedError
from app.core.ratelimit import SlidingWindowLimiter
from app.core.security import validate_client_id
from app.db.repository import SqlScanRepository
from app.db.session import get_db

_analyze_requests, _analyze_window = analyze_rate_limit()
_default_requests, _default_window = default_rate_limit()

analyze_limiter = SlidingWindowLimiter(_analyze_requests, _analyze_window)
default_limiter = SlidingWindowLimiter(_default_requests, _default_window)


def reset_rate_limiters() -> None:
    """Test helper - clears every bucket."""
    analyze_limiter.reset()
    default_limiter.reset()


def client_ip(request: Request) -> str:
    # Behind a proxy the platform sets X-Forwarded-For; take the first hop.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    return (request.client.host if request.client else "unknown")[:64]


def rate_limit_analyze(request: Request) -> None:
    allowed, retry_after = analyze_limiter.check(f"analyze:{client_ip(request)}")
    if not allowed:
        raise RateLimitedError(
            "Too many scans from this connection. Please wait a moment and try again.",
            details={"retry_after_seconds": retry_after},
        )


def rate_limit_default(request: Request) -> None:
    allowed, retry_after = default_limiter.check(f"default:{client_ip(request)}")
    if not allowed:
        raise RateLimitedError(
            "Too many requests from this connection. Please slow down.",
            details={"retry_after_seconds": retry_after},
        )


def get_client_id(
    x_client_id: str | None = Header(default=None, alias="X-Client-Id"),
) -> str | None:
    """Anonymous, browser generated identifier. Never an account or email."""
    return validate_client_id(x_client_id)


def get_repository(db: Session = Depends(get_db)) -> SqlScanRepository:
    return SqlScanRepository(db)
