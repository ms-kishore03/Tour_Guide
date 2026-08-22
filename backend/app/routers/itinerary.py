from fastapi import APIRouter

from app.deps import CurrentUser, Db
from app.schemas.itinerary import ItineraryResponse, TodoCreate
from app.services import itinerary_service

router = APIRouter(prefix="/trips/{place}/itinerary", tags=["itinerary"])


@router.get("", response_model=ItineraryResponse)
async def get_itinerary(place: str, user: CurrentUser, db: Db) -> ItineraryResponse:
    itinerary_by_date = await itinerary_service.get_itinerary(db, user.username, place)
    return ItineraryResponse(itinerary_by_date=itinerary_by_date)


@router.get("/todo", response_model=list[str])
async def get_todo(place: str, user: CurrentUser, db: Db) -> list[str]:
    return await itinerary_service.get_todos(db, user.username, place)


@router.post("/todo", response_model=list[str])
async def add_todo(place: str, payload: TodoCreate, user: CurrentUser, db: Db) -> list[str]:
    return await itinerary_service.add_todo(db, user.username, place, payload.task)
