import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

TEST_STORE_DIR = BACKEND_DIR / "store" / "test"
TEST_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Must be set before any `app.*` module is imported, since config.py reads
# these at import time.
os.environ["SQLITE_PATH"] = str(TEST_STORE_DIR / "test_fri.db")
os.environ["USE_LLM"] = "0"

from data import ingest  # noqa: E402
from app.db import SessionLocal  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _seed_once():
    ingest.run()
    yield


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c
