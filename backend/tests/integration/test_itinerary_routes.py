import pytest

from app.core.security import create_access_token
from app.schemas.common import UserContext
from app.services import auth_service


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {create_access_token('alice')}"}


@pytest.fixture(autouse=True)
def patch_current_user(monkeypatch):
    async def fake_get_current_user(username):
        return UserContext(username=username, email="alice@example.com")

    monkeypatch.setattr(auth_service, "get_current_user", fake_get_current_user)


async def test_get_itinerary_requires_auth(client):
    res = await client.get("/api/v1/trips/Kyoto/itinerary")
    assert res.status_code == 401


async def test_get_itinerary_returns_full_grouped_days(client, auth_headers, override_db):
    await override_db["itinerary"].insert_one(
        {
            "username": "alice",
            "place": "Kyoto",
            "itinerary_by_date": {
                "01/01/2026": [
                    {"location": "Fushimi Inari", "time": "09:00 AM"},
                    {"location": "Kiyomizu-dera", "time": "01:00 PM"},
                ]
            },
        }
    )
    res = await client.get("/api/v1/trips/Kyoto/itinerary", headers=auth_headers)
    assert res.status_code == 200
    day = res.json()["itinerary_by_date"]["01/01/2026"]
    assert len(day) == 2


async def test_todo_add_and_list_roundtrip(client, auth_headers):
    add_res = await client.post(
        "/api/v1/trips/Kyoto/itinerary/todo", json={"task": "Buy JR pass"}, headers=auth_headers
    )
    assert add_res.status_code == 200
    assert add_res.json() == ["Buy JR pass"]

    list_res = await client.get("/api/v1/trips/Kyoto/itinerary/todo", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json() == ["Buy JR pass"]
