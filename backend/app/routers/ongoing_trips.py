from fastapi import APIRouter, HTTPException

from app.deps import CurrentUser, Db
from app.schemas.ongoing_trip import ExpenseCreate, MessageResponse, OngoingTripResponse
from app.services import ongoing_trip_service

router = APIRouter(prefix="/ongoing-trips", tags=["ongoing-trips"])


@router.post("/{place}/start", response_model=MessageResponse)
async def start(place: str, user: CurrentUser, db: Db) -> MessageResponse:
    await ongoing_trip_service.start_ongoing_trip(db, user.username, place)
    return MessageResponse(message="Trip started")


@router.get("", response_model=OngoingTripResponse | None)
async def get_ongoing(user: CurrentUser, db: Db) -> OngoingTripResponse | None:
    doc = await ongoing_trip_service.get_ongoing_trip(db, user.username)
    if doc is None:
        return None
    return OngoingTripResponse(**doc)


@router.post("/{place}/end", response_model=MessageResponse)
async def end(place: str, user: CurrentUser, db: Db) -> MessageResponse:
    await ongoing_trip_service.end_ongoing_trip(db, user.username, place)
    return MessageResponse(message="Trip ended")


@router.get("/{place}/expenses", response_model=list[dict])
async def list_expenses(place: str, user: CurrentUser, db: Db) -> list[dict]:
    return await ongoing_trip_service.get_expenses(db, user.username, place)


@router.post("/{place}/expenses", response_model=list[dict])
async def add_expense(place: str, payload: ExpenseCreate, user: CurrentUser, db: Db) -> list[dict]:
    if payload.amount < 0:
        raise HTTPException(422, detail="Amount must be non-negative")
    return await ongoing_trip_service.add_expense(db, user.username, place, payload.model_dump())
