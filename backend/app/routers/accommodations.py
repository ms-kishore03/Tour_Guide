from fastapi import APIRouter

from app.schemas.accommodation import AccommodationSearchRequest, AccommodationSearchResponse
from app.services import hotel_service

router = APIRouter(prefix="/accommodations", tags=["accommodations"])


@router.post("/search", response_model=AccommodationSearchResponse)
async def search(payload: AccommodationSearchRequest) -> AccommodationSearchResponse:
    results = await hotel_service.search_accommodations(payload.location, payload.checkin, payload.checkout)
    return AccommodationSearchResponse(results=results)
