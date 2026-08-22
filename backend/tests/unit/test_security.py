import time

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret!")
    assert verify_password("s3cret!", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_roundtrip():
    token = create_access_token("alice")
    payload = decode_token(token)
    assert payload["sub"] == "alice"
    assert payload["type"] == "access"


def test_refresh_token_has_jti_and_expiry():
    token, jti, expires_at = create_refresh_token("alice")
    payload = decode_token(token)
    assert payload["jti"] == jti
    assert payload["type"] == "refresh"
    assert expires_at.timestamp() == pytest.approx(payload["exp"], abs=1)


def test_decode_token_rejects_garbage():
    with pytest.raises(ValueError):
        decode_token("not-a-jwt")


def test_decode_token_rejects_expired(monkeypatch):
    import app.core.security as security_module

    monkeypatch.setattr(security_module.settings, "access_token_expire_minutes", -1)
    token = create_access_token("alice")
    with pytest.raises(ValueError):
        decode_token(token)
