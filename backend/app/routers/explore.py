from fastapi import APIRouter

from app.schemas.trip import ExploreRequest, ExploreResponse
from app.services import trip_service

router = APIRouter(prefix="/explore", tags=["explore"])


@router.post("", response_model=ExploreResponse)
async def explore(payload: ExploreRequest) -> ExploreResponse:
    suggestions = await trip_service.suggest_places(
        payload.trip_theme,
        payload.activity,
        payload.climate,
        payload.budget,
        payload.duration,
        payload.location,
        payload.trip_type,
        payload.transport,
    )
    return ExploreResponse(places=suggestions)
