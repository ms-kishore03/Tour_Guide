from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    weather_data: str | None = None
    geoapify_data: list[str] | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    ts: datetime
    partial: bool = False


class ChatResponse(BaseModel):
    message: str
    draft_itinerary: list[dict] | None = None
    status: str | None = None
    day_summary: dict | None = None
