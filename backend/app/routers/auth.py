from fastapi import APIRouter, Request

from app.core.rate_limit import limiter
from app.deps import CurrentUser, Db
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse)
@limiter.limit("5/minute")
async def register(request: Request, payload: RegisterRequest) -> MessageResponse:
    message = await auth_service.register(
        payload.username, payload.password, payload.confirm_password, payload.email
    )
    return MessageResponse(message=message)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, db: Db) -> TokenResponse:
    return await auth_service.login(db, payload.username, payload.password)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
async def refresh(request: Request, payload: RefreshRequest, db: Db) -> TokenResponse:
    return await auth_service.refresh(db, payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse(username=user.username, email=user.email)


@router.post("/logout", response_model=MessageResponse)
async def logout(user: CurrentUser, db: Db) -> MessageResponse:
    await auth_service.logout(db, user.username)
    return MessageResponse(message="Logged out")
