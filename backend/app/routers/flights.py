from fastapi import APIRouter

from app.schemas.flight import FlightSearchRequest, FlightSearchResponse
from app.services import flight_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/search", response_model=FlightSearchResponse)
async def search(payload: FlightSearchRequest) -> FlightSearchResponse:
    flights = await flight_service.search_flights(
        payload.departure,
        payload.arrival,
        payload.outbound_date,
        payload.return_date,
        payload.currency,
        payload.travel_class,
        payload.trip_type,
        payload.adults,
        payload.children,
        payload.infants_in_seat,
        payload.infants_in_lap,
    )
    return FlightSearchResponse(flights=flights)
