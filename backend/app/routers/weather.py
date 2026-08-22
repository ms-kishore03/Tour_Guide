from fastapi import APIRouter

from app.schemas.weather import WeatherResponse
from app.services import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/{place}", response_model=WeatherResponse)
async def get_weather(place: str, lat: float | None = None, lon: float | None = None) -> WeatherResponse:
    return await weather_service.get_weather(place, lat, lon)
