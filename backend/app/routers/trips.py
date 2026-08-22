from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUser, Db
from app.schemas.trip import MessageResponse, SaveTripRequest, TripResponse
from app.services import trip_service

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripResponse)
async def save_trip(payload: SaveTripRequest, user: CurrentUser, db: Db) -> TripResponse:
    trip_dict = payload.to_legacy_dict()
    status_result = await trip_service.save_trip(db, user.username, trip_dict)
    if status_result == "exists":
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Trip already saved")
    return TripResponse.from_legacy_dict(trip_dict)


@router.get("", response_model=list[TripResponse])
async def list_trips(user: CurrentUser, db: Db) -> list[TripResponse]:
    return await trip_service.get_saved_trips(db, user.username)


@router.get("/{place_name}", response_model=TripResponse)
async def get_trip(place_name: str, user: CurrentUser, db: Db) -> TripResponse:
    trip = await trip_service.get_saved_trip(db, user.username, place_name)
    if trip is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@router.delete("/{place_name}", response_model=MessageResponse)
async def delete_trip(place_name: str, user: CurrentUser, db: Db) -> MessageResponse:
    deleted = await trip_service.delete_saved_trip(db, user.username, place_name)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return MessageResponse(message="Trip deleted")


@router.post("/{place_name}/plan", response_model=MessageResponse)
async def start_planning(place_name: str, user: CurrentUser, db: Db) -> MessageResponse:
    ok = await trip_service.start_planning(db, user.username, place_name)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Trip not found in saved trips")
    return MessageResponse(message="Planning started")
