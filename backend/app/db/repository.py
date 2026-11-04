"""Repository layer.

``ScanRepository`` is the only interface the services use, which keeps the
storage engine swappable (SQLite today, PostgreSQL later) without touching
business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import Scan


@dataclass(frozen=True)
class ScanRecord:
    id: str
    client_id: str
    scan_type: str
    channel: str
    risk_score: int
    risk_level: str
    category: str
    category_label: str
    confidence: float
    excerpt: str
    content_hash: str
    payload: str
    created_at: datetime


class ScanRepository(Protocol):
    def add(self, record: ScanRecord) -> ScanRecord: ...
    def get(self, scan_id: str, client_id: str) -> ScanRecord | None: ...
    def list(self, client_id: str, limit: int, offset: int, risk_level: str | None = None) -> Sequence[ScanRecord]: ...
    def delete(self, scan_id: str, client_id: str) -> bool: ...
    def count(self, client_id: str) -> int: ...
    def stats(self, client_id: str) -> dict: ...


def _to_record(row: Scan) -> ScanRecord:
    return ScanRecord(
        id=row.id,
        client_id=row.client_id,
        scan_type=row.scan_type,
        channel=row.channel,
        risk_score=row.risk_score,
        risk_level=row.risk_level,
        category=row.category,
        category_label=row.category_label,
        confidence=row.confidence,
        excerpt=row.excerpt,
        content_hash=row.content_hash,
        payload=row.payload,
        created_at=row.created_at,
    )


class SqlScanRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, record: ScanRecord) -> ScanRecord:
        row = Scan(
            id=record.id,
            client_id=record.client_id,
            scan_type=record.scan_type,
            channel=record.channel,
            risk_score=record.risk_score,
            risk_level=record.risk_level,
            category=record.category,
            category_label=record.category_label,
            confidence=record.confidence,
            excerpt=record.excerpt,
            content_hash=record.content_hash,
            payload=record.payload,
            created_at=record.created_at,
        )
        self._db.add(row)
        self._db.commit()
        self._db.refresh(row)
        return _to_record(row)

    def get(self, scan_id: str, client_id: str) -> ScanRecord | None:
        row = self._db.get(Scan, scan_id)
        if row is None or row.client_id != client_id:
            return None
        return _to_record(row)

    def list(
        self, client_id: str, limit: int, offset: int, risk_level: str | None = None
    ) -> Sequence[ScanRecord]:
        stmt = select(Scan).where(Scan.client_id == client_id)
        if risk_level:
            stmt = stmt.where(Scan.risk_level == risk_level)
        stmt = stmt.order_by(Scan.created_at.desc()).limit(limit).offset(offset)
        return [_to_record(row) for row in self._db.execute(stmt).scalars().all()]

    def delete(self, scan_id: str, client_id: str) -> bool:
        result = self._db.execute(
            delete(Scan).where(Scan.id == scan_id, Scan.client_id == client_id)
        )
        self._db.commit()
        return bool(result.rowcount)

    def count(self, client_id: str) -> int:
        stmt = select(func.count(Scan.id)).where(Scan.client_id == client_id)
        return int(self._db.execute(stmt).scalar_one())

    def stats(self, client_id: str) -> dict:
        total = self.count(client_id)
        by_level = {
            level: int(count)
            for level, count in self._db.execute(
                select(Scan.risk_level, func.count(Scan.id))
                .where(Scan.client_id == client_id)
                .group_by(Scan.risk_level)
            ).all()
        }
        by_category = [
            {"category": cat, "label": label, "count": int(count)}
            for cat, label, count in self._db.execute(
                select(Scan.category, Scan.category_label, func.count(Scan.id))
                .where(Scan.client_id == client_id)
                .group_by(Scan.category, Scan.category_label)
                .order_by(func.count(Scan.id).desc())
            ).all()
        ]
        recent = self.list(client_id=client_id, limit=5, offset=0)
        return {
            "total_scans": total,
            "by_risk_level": by_level,
            "by_category": by_category,
            "recent": recent,
        }
