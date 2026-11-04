"""Database abstraction.

The application talks to the persistence layer through the ``ScanRepository``
protocol in ``repository.py``.  ``SQLAlchemy`` is used as the default engine so
the same code runs on SQLite (default) and PostgreSQL (set ``DATABASE_URL``).
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        # check_same_thread=False is required because FastAPI runs sync
        # dependencies in a thread pool.
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


settings = get_settings()
engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    from app.db import models  # noqa: F401  (register mappings)

    Base.metadata.create_all(bind=engine)
