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


async def test_ongoing_trip_full_lifecycle(client, auth_headers):
    start_res = await client.post("/api/v1/ongoing-trips/Kyoto/start", headers=auth_headers)
    assert start_res.status_code == 200

    get_res = await client.get("/api/v1/ongoing-trips", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["place"] == "Kyoto"

    add_res = await client.post(
        "/api/v1/ongoing-trips/Kyoto/expenses",
        json={"amount": 20, "category": "Food", "date": "01/01/2026"},
        headers=auth_headers,
    )
    assert add_res.status_code == 200
    assert len(add_res.json()) == 1

    list_res = await client.get("/api/v1/ongoing-trips/Kyoto/expenses", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()[0]["amount"] == 20

    end_res = await client.post("/api/v1/ongoing-trips/Kyoto/end", headers=auth_headers)
    assert end_res.status_code == 200

    after_end = await client.get("/api/v1/ongoing-trips", headers=auth_headers)
    assert after_end.json() is None


async def test_add_expense_rejects_negative_amount(client, auth_headers):
    res = await client.post(
        "/api/v1/ongoing-trips/Kyoto/expenses",
        json={"amount": -5, "category": "Food", "date": "01/01/2026"},
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_ongoing_trips_require_auth(client):
    res = await client.get("/api/v1/ongoing-trips")
    assert res.status_code == 401
