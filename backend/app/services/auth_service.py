from datetime import datetime, timezone

import bcrypt
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.mongo import REFRESH_TOKENS
from app.schemas.auth import TokenResponse
from app.schemas.common import UserContext

from Utilities import User_Authentication as legacy_auth  # noqa: E402


async def register(username: str, password: str, confirm_password: str, email: str) -> str:
    message = await run_in_threadpool(
        legacy_auth.register, username, password, confirm_password, email
    )
    if message != "User registered successfully!":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=message)
    return message


async def _authenticate(username: str, password: str) -> dict:
    user_doc = await run_in_threadpool(legacy_auth.get_user, username)
    if not user_doc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    stored_hash = user_doc["password"]
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    return user_doc


async def login(db: AsyncIOMotorDatabase, username: str, password: str) -> TokenResponse:
    user_doc = await _authenticate(username, password)
    return await _issue_tokens(db, user_doc["username"])


async def _issue_tokens(db: AsyncIOMotorDatabase, username: str) -> TokenResponse:
    access_token = create_access_token(username)
    refresh_token, jti, expires_at = create_refresh_token(username)
    await db[REFRESH_TOKENS].insert_one(
        {"jti": jti, "username": username, "expires_at": expires_at, "revoked": False}
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh(db: AsyncIOMotorDatabase, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    jti = payload.get("jti")
    record = await db[REFRESH_TOKENS].find_one({"jti": jti})
    if not record or record.get("revoked"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
    if record["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    await db[REFRESH_TOKENS].update_one({"jti": jti}, {"$set": {"revoked": True}})
    return await _issue_tokens(db, payload["sub"])


async def logout(db: AsyncIOMotorDatabase, username: str) -> None:
    await db[REFRESH_TOKENS].update_many(
        {"username": username, "revoked": False}, {"$set": {"revoked": True}}
    )


async def get_current_user(username: str) -> UserContext:
    user_doc = await run_in_threadpool(legacy_auth.get_user, username)
    if not user_doc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserContext(username=user_doc["username"], email=user_doc["email"])
