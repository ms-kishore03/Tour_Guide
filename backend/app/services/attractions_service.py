from datetime import datetime, timedelta, timezone

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.llm import get_llm
from app.core.metrics import track_external_api_call, track_llm_call
from app.db.mongo import THINGS_TO_DO
from app.schemas.attractions import GeoResponse

from cognix_ai.tools.attractions_tool import select_top_attractions  # noqa: E402

THINGS_TO_DO_TTL = timedelta(weeks=2)


async def _geoapify_attractions(place: str) -> tuple[float, float, list[str]] | None:
    """Async-native reimplementation of API_Handlers/geoapify.py::geoapify_attractions.

    The legacy function stays sync/untouched for the Streamlit app; this is the
    FastAPI hot path, using httpx instead of requests + run_in_threadpool.
    """
    api_key = get_settings().geoapify_api_key
    async with httpx.AsyncClient(timeout=10) as client:
        geo_resp = await client.get(
            "https://api.geoapify.com/v1/geocode/search",
            params={"text": place, "format": "json", "apiKey": api_key},
        )
        geo_data = geo_resp.json()
        results = geo_data.get("results")
        if not results:
            return None
        lat, lon = results[0]["lat"], results[0]["lon"]

        places_resp = await client.get(
            "https://api.geoapify.com/v2/places",
            params={
                "categories": "tourism.attraction,tourism.sights",
                "filter": f"circle:{lon},{lat},5000",
                "limit": 30,
                "apiKey": api_key,
            },
        )
        features = places_resp.json().get("features", [])

    attractions = [
        name
        for f in features
        if (name := f.get("properties", {}).get("name"))
    ]
    return lat, lon, attractions


async def get_geo(place: str) -> GeoResponse:
    with track_external_api_call("geoapify"):
        result = await _geoapify_attractions(place)
    if not result:
        return GeoResponse(lat=None, lon=None, raw=[])
    lat, lon, raw = result
    return GeoResponse(lat=lat, lon=lon, raw=raw)


async def get_attractions(db: AsyncIOMotorDatabase, place: str) -> tuple[str, list[str]]:
    """Returns (status, places), mirroring the legacy Things_To_Do cache semantics."""
    entry = await db[THINGS_TO_DO].find_one({"destination": place})
    if entry:
        updated_at = entry.get("timestamp")
        if updated_at:
            if updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - updated_at <= THINGS_TO_DO_TTL:
                return "ok", entry.get("interests", [])
        await db[THINGS_TO_DO].delete_one({"_id": entry["_id"]})

    geo = await get_geo(place)
    if not geo.raw:
        return "error", []

    with track_llm_call("attraction_selector"):
        attractions = await run_in_threadpool(
            select_top_attractions,
            "",
            {"place": place, "geoapify_data": geo.raw, "llm": get_llm()},
        )
    if attractions:
        await db[THINGS_TO_DO].insert_one(
            {"destination": place, "interests": attractions, "timestamp": datetime.now(timezone.utc)}
        )
        return "ok", attractions

    return "error", []
