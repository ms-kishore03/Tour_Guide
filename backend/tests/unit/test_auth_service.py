import bcrypt
import pytest
from fastapi import HTTPException
from mongomock_motor import AsyncMongoMockClient

from app.services import auth_service
from Utilities import User_Authentication as legacy_auth


@pytest.fixture
def db():
    return AsyncMongoMockClient()["Tour_Guide_Test"]


async def test_register_rejects_duplicate_username(monkeypatch):
    monkeypatch.setattr(legacy_auth, "register", lambda *a, **kw: "Username already exists! Please log in instead.")
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register("alice", "pw123456", "pw123456", "alice@example.com")
    assert exc_info.value.status_code == 400


async def test_register_success_passthrough(monkeypatch):
    monkeypatch.setattr(legacy_auth, "register", lambda *a, **kw: "User registered successfully!")
    message = await auth_service.register("alice", "pw123456", "pw123456", "alice@example.com")
    assert message == "User registered successfully!"


async def test_login_wrong_password_raises_401(monkeypatch, db):
    hashed = bcrypt.hashpw(b"correct-pw", bcrypt.gensalt())
    monkeypatch.setattr(
        legacy_auth, "get_user", lambda username: {"username": "alice", "password": hashed, "email": "a@b.com"}
    )
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(db, "alice", "wrong-pw")
    assert exc_info.value.status_code == 401


async def test_login_unknown_user_raises_401(monkeypatch, db):
    monkeypatch.setattr(legacy_auth, "get_user", lambda username: None)
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login(db, "ghost", "whatever")
    assert exc_info.value.status_code == 401


async def test_login_success_issues_tokens(monkeypatch, db):
    hashed = bcrypt.hashpw(b"correct-pw", bcrypt.gensalt())
    monkeypatch.setattr(
        legacy_auth, "get_user", lambda username: {"username": "alice", "password": hashed, "email": "a@b.com"}
    )
    tokens = await auth_service.login(db, "alice", "correct-pw")
    assert tokens.access_token
    assert tokens.refresh_token
    stored = await db["RefreshTokens"].find_one({"username": "alice"})
    assert stored is not None
    assert stored["revoked"] is False


async def test_refresh_rotates_token(monkeypatch, db):
    hashed = bcrypt.hashpw(b"correct-pw", bcrypt.gensalt())
    monkeypatch.setattr(
        legacy_auth, "get_user", lambda username: {"username": "alice", "password": hashed, "email": "a@b.com"}
    )
    tokens = await auth_service.login(db, "alice", "correct-pw")
    new_tokens = await auth_service.refresh(db, tokens.refresh_token)
    assert new_tokens.refresh_token != tokens.refresh_token

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.refresh(db, tokens.refresh_token)
    assert exc_info.value.status_code == 401
