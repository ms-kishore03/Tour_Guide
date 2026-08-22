import asyncio

import httpx
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.llm import get_llm
from app.core.metrics import track_external_api_call, track_llm_call
from app.schemas.weather import WeatherResponse
from app.services.attractions_service import get_geo

from cognix_ai.tools.Weather_tool import Weather_Explainer_Agent  # noqa: E402


async def _weather_report(lat: float, lon: float, city: str) -> tuple[str, list[dict]]:
    """Async-native reimplementation of API_Handlers/WeatherHandler.py::weather_report.

    Legacy module stays sync/untouched for the Streamlit app; this is the
    FastAPI hot path, using httpx instead of requests + run_in_threadpool.
    """
    api_key = get_settings().openweathermap_api_key
    async with httpx.AsyncClient(timeout=10) as client:
        current_resp, forecast_resp = await asyncio.gather(
            client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"lat": lat, "lon": lon, "appid": api_key},
            ),
            client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={"lat": lat, "lon": lon, "appid": api_key},
            ),
        )
    current_data = current_resp.json()
    forecast_data = forecast_resp.json()

    if "weather" not in current_data:
        current = f"Could not retrieve weather for {city}. Response: {current_data}"
    else:
        current = (
            f"The weather in {city} is {current_data['weather'][0]['description']} with "
            f"temperature {current_data['main']['temp']} K, humidity {current_data['main']['humidity']}%, "
            f"max {current_data['main']['temp_max']} K, min {current_data['main']['temp_min']} K. "
            f"(lat: {lat}, lon: {lon})"
        )

    if "list" not in forecast_data:
        forecast = f"Could not retrieve forecast for {city}. Response: {forecast_data}"
    else:
        forecast = [
            {
                "datetime": f["dt_txt"],
                "temperature": f["main"]["temp"],
                "weather": f["weather"][0]["description"],
                "humidity": f["main"]["humidity"],
            }
            for f in forecast_data["list"]
        ]

    return current, forecast


def _geocode_sync(place: str) -> tuple[float | None, float | None]:
    try:
        geolocator = Nominatim(user_agent="tour_guide_backend")
        location = geolocator.geocode(place, timeout=10)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    return None, None


async def get_weather(place: str, lat: float | None = None, lon: float | None = None) -> WeatherResponse:
    if lat is None or lon is None:
        lat, lon = await run_in_threadpool(_geocode_sync, place)
        if lat is None or lon is None:
            geo = await get_geo(place)
            lat, lon = geo.lat, geo.lon

    with track_external_api_call("openweathermap"):
        current, forecast = await _weather_report(lat, lon, place)

    with track_llm_call("weather_explainer"):
        explanation = await run_in_threadpool(
            Weather_Explainer_Agent,
            "",
            {"place": place, "weather_data": [current, forecast], "llm": get_llm()},
        )

    return WeatherResponse(explanation=explanation, current=current, forecast=forecast)
