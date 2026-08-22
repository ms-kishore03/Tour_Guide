import pytest
from mongomock_motor import AsyncMongoMockClient

from app.services import trip_service

TRIP = {
    "Place Name": "Kyoto",
    "Scenario": "Cultural",
    "Climate": "Mild",
    "Duration": "5 days",
    "People": "2",
    "Transport": "Flight",
    "Description": "Historic temples and gardens.",
}


@pytest.fixture
def db():
    return AsyncMongoMockClient()["Tour_Guide_Test"]


async def test_save_trip_is_idempotent(db):
    first = await trip_service.save_trip(db, "alice", TRIP)
    assert first == "saved"
    second = await trip_service.save_trip(db, "alice", TRIP)
    assert second == "exists"


async def test_get_saved_trips_scoped_to_username(db):
    await trip_service.save_trip(db, "alice", TRIP)
    other_trip = {**TRIP, "Place Name": "Osaka"}
    await trip_service.save_trip(db, "bob", other_trip)

    alice_trips = await trip_service.get_saved_trips(db, "alice")
    assert len(alice_trips) == 1
    assert alice_trips[0].place_name == "Kyoto"


async def test_delete_saved_trip(db):
    await trip_service.save_trip(db, "alice", TRIP)
    deleted = await trip_service.delete_saved_trip(db, "alice", "Kyoto")
    assert deleted is True
    again = await trip_service.delete_saved_trip(db, "alice", "Kyoto")
    assert again is False


async def test_start_planning_requires_saved_trip(db):
    ok = await trip_service.start_planning(db, "alice", "Nowhere")
    assert ok is False

    await trip_service.save_trip(db, "alice", TRIP)
    ok = await trip_service.start_planning(db, "alice", "Kyoto")
    assert ok is True


async def test_suggest_places_uses_cache(monkeypatch):
    called = {"gemini": False}

    def fake_suggest_places(*args, **kwargs):
        called["gemini"] = True
        return ["Kyoto"], ["A historic city."]

    monkeypatch.setattr(trip_service, "legacy_suggest_places", fake_suggest_places)

    suggestions = await trip_service.suggest_places(
        "Cultural", "Sightseeing", "Mild", "Medium", "5 days", "Japan", "Leisure", "Flight"
    )
    assert called["gemini"] is True
    assert suggestions[0].name == "Kyoto"
    assert suggestions[0].description == "A historic city."
