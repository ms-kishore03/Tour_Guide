from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.rate_limit import limiter
from app.deps import CurrentUser, Db, RagFn
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{place}", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request, place: str, payload: ChatRequest, user: CurrentUser, db: Db, rag_fn: RagFn
) -> ChatResponse:
    return await chat_service.run_chat(
        db, user.username, place, payload.message, payload.weather_data, payload.geoapify_data, rag_fn
    )


@router.post("/{place}/stream")
@limiter.limit("20/minute")
async def chat_stream(
    request: Request, place: str, payload: ChatRequest, user: CurrentUser, db: Db, rag_fn: RagFn
) -> StreamingResponse:
    generator = chat_service.run_chat_stream(
        db, user.username, place, payload.message, payload.weather_data, payload.geoapify_data, rag_fn
    )
    return StreamingResponse(generator, media_type="text/event-stream")


@router.get("/{place}/history", response_model=list[ChatMessage])
async def history(place: str, user: CurrentUser, db: Db) -> list[ChatMessage]:
    return await chat_service.get_history(db, user.username, place)
