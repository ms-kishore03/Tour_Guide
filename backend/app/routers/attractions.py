from fastapi import APIRouter

from app.deps import Db
from app.schemas.attractions import AttractionsResponse, GeoResponse
from app.services import attractions_service

router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("/{place}", response_model=AttractionsResponse)
async def get_attractions(place: str, db: Db) -> AttractionsResponse:
    status_result, places = await attractions_service.get_attractions(db, place)
    return AttractionsResponse(status=status_result, places=places)


@router.get("/{place}/geo", response_model=GeoResponse)
async def get_geo(place: str) -> GeoResponse:
    return await attractions_service.get_geo(place)
