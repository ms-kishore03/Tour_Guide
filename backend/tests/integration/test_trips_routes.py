import pytest

from app.core.security import create_access_token

TRIP_PAYLOAD = {
    "place_name": "Kyoto",
    "scenario": "Cultural",
    "climate": "Mild",
    "duration": "5 days",
    "people": "2",
    "transport": "Flight",
    "description": "Historic temples and gardens.",
}


@pytest.fixture
def auth_headers():
    token = create_access_token("alice")
    return {"Authorization": f"Bearer {token}"}


async def test_trips_requires_auth(client):
    res = await client.get("/api/v1/trips")
    assert res.status_code == 401


async def test_save_list_get_delete_trip_roundtrip(client, auth_headers, monkeypatch):
    from app.services import auth_service

    async def fake_get_current_user(username):
        from app.schemas.common import UserContext

        return UserContext(username=username, email="alice@example.com")

    monkeypatch.setattr(auth_service, "get_current_user", fake_get_current_user)

    save_res = await client.post("/api/v1/trips", json=TRIP_PAYLOAD, headers=auth_headers)
    assert save_res.status_code == 200
    assert save_res.json()["place_name"] == "Kyoto"

    # saving the identical trip again should conflict
    dup_res = await client.post("/api/v1/trips", json=TRIP_PAYLOAD, headers=auth_headers)
    assert dup_res.status_code == 409

    list_res = await client.get("/api/v1/trips", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = await client.get("/api/v1/trips/Kyoto", headers=auth_headers)
    assert get_res.status_code == 200

    plan_res = await client.post("/api/v1/trips/Kyoto/plan", headers=auth_headers)
    assert plan_res.status_code == 200

    delete_res = await client.delete("/api/v1/trips/Kyoto", headers=auth_headers)
    assert delete_res.status_code == 200

    missing_res = await client.get("/api/v1/trips/Kyoto", headers=auth_headers)
    assert missing_res.status_code == 404


async def test_delete_nonexistent_trip_returns_404(client, auth_headers, monkeypatch):
    from app.services import auth_service
    from app.schemas.common import UserContext

    async def fake_get_current_user(username):
        return UserContext(username=username, email="alice@example.com")

    monkeypatch.setattr(auth_service, "get_current_user", fake_get_current_user)

    res = await client.delete("/api/v1/trips/Atlantis", headers=auth_headers)
    assert res.status_code == 404
