from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx
from mongomock_motor import AsyncMongoMockClient

from app.services import attractions_service
from app.schemas.attractions import GeoResponse


@pytest.fixture
def db():
    return AsyncMongoMockClient()["Tour_Guide_Test"]


async def test_get_attractions_uses_fresh_cache(db):
    await db["Things_To_Do"].insert_one(
        {"destination": "Kyoto", "interests": ["Fushimi Inari"], "timestamp": datetime.now(timezone.utc)}
    )
    status, places = await attractions_service.get_attractions(db, "Kyoto")
    assert status == "ok"
    assert places == ["Fushimi Inari"]


async def test_get_attractions_evicts_stale_cache(db, monkeypatch):
    stale = datetime.now(timezone.utc) - timedelta(weeks=3)
    await db["Things_To_Do"].insert_one({"destination": "Kyoto", "interests": ["Old Data"], "timestamp": stale})

    async def fake_get_geo(place):
        return GeoResponse(lat=35.0, lon=135.7, raw=["Fushimi Inari Shrine"])

    monkeypatch.setattr(attractions_service, "get_geo", fake_get_geo)
    monkeypatch.setattr(
        attractions_service, "select_top_attractions", lambda *a, **kw: ["Fushimi Inari Shrine"]
    )

    status, places = await attractions_service.get_attractions(db, "Kyoto")
    assert status == "ok"
    assert places == ["Fushimi Inari Shrine"]

    remaining = await db["Things_To_Do"].find_one({"destination": "Kyoto"})
    assert remaining["interests"] == ["Fushimi Inari Shrine"]


async def test_get_attractions_returns_error_when_geocoding_fails(db, monkeypatch):
    async def fake_get_geo(place):
        return GeoResponse(lat=None, lon=None, raw=[])

    monkeypatch.setattr(attractions_service, "get_geo", fake_get_geo)

    status, places = await attractions_service.get_attractions(db, "Nowhere")
    assert status == "error"
    assert places == []


@respx.mock
async def test_get_geo_calls_geoapify_over_httpx():
    respx.get("https://api.geoapify.com/v1/geocode/search").mock(
        return_value=httpx.Response(200, json={"results": [{"lat": 35.0, "lon": 135.7}]})
    )
    respx.get("https://api.geoapify.com/v2/places").mock(
        return_value=httpx.Response(
            200, json={"features": [{"properties": {"name": "Fushimi Inari Shrine"}}]}
        )
    )

    geo = await attractions_service.get_geo("Kyoto")
    assert geo.lat == 35.0
    assert geo.lon == 135.7
    assert geo.raw == ["Fushimi Inari Shrine"]


@respx.mock
async def test_get_geo_returns_empty_when_geocoding_has_no_results():
    respx.get("https://api.geoapify.com/v1/geocode/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )

    geo = await attractions_service.get_geo("Nowhere")
    assert geo.lat is None
    assert geo.raw == []
