from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_token
from app.db.mongo import get_database
from app.schemas.common import UserContext
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> AsyncIOMotorDatabase:
    return get_database()


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> UserContext:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return await auth_service.get_current_user(payload["sub"])


def get_rag_fn(request: Request) -> Callable[[str], str] | None:
    return getattr(request.app.state, "rag_fn", None)


CurrentUser = Annotated[UserContext, Depends(get_current_user)]
Db = Annotated[AsyncIOMotorDatabase, Depends(get_db)]
RagFn = Annotated[Callable[[str], str] | None, Depends(get_rag_fn)]
