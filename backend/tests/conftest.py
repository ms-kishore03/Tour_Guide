import os
import sys
from pathlib import Path

os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.core.rate_limit import limiter
from app.deps import get_db
from app.main import app


@pytest.fixture
def mock_db():
    client = AsyncMongoMockClient()
    return client["Tour_Guide_Test"]


@pytest.fixture
def override_db(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client(override_db):
    limiter.reset()  # every test gets a clean rate-limit bucket (all test requests share 127.0.0.1)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
