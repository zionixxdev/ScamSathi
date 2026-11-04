"""ORM models.

Only derived and redacted data is ever persisted: a short redacted excerpt,
the computed risk fields and a salted hash of the original content.  Raw
message bodies, OTPs, passwords and account numbers are never stored.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    scan_type: Mapped[str] = mapped_column(String(16), nullable=False)  # message | url
    channel: Mapped[str] = mapped_column(String(16), nullable=False, default="other")
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(48), nullable=False)
    category_label: Mapped[str] = mapped_column(String(96), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, index=True)
