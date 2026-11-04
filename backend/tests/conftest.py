"""Test configuration.

A throwaway SQLite database is used and the environment is configured before the
application package is imported, so the cached settings pick it up.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path

import pytest

TEST_DB = Path(tempfile.gettempdir()) / f"scamsathi_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["APP_ENV"] = "test"
os.environ["AI_PROVIDER"] = "none"
os.environ["URL_REPUTATION_PROVIDER"] = "none"
os.environ["RATE_LIMIT_ANALYZE"] = "30/60"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
    TEST_DB.unlink(missing_ok=True)


@pytest.fixture()
def client_id() -> str:
    return "testclient" + uuid.uuid4().hex[:12]


@pytest.fixture()
def headers(client_id: str) -> dict:
    return {"X-Client-Id": client_id}
