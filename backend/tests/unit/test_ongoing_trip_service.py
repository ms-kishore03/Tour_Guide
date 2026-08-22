import pytest
from mongomock_motor import AsyncMongoMockClient

from app.services import ongoing_trip_service, trip_service

TRIP = {
    "Place Name": "Kyoto",
    "Scenario": "Cultural",
    "Climate": "Mild",
    "Duration": "5 days",
    "People": "2",
    "Transport": "Flight",
    "Description": "Historic temples.",
}


@pytest.fixture
def db():
    return AsyncMongoMockClient()["Tour_Guide_Test"]


async def test_start_ongoing_trip_copies_saved_trip_details(db):
    await trip_service.save_trip(db, "alice", TRIP)
    await ongoing_trip_service.start_ongoing_trip(db, "alice", "Kyoto")

    doc = await ongoing_trip_service.get_ongoing_trip(db, "alice")
    assert doc["place"] == "Kyoto"
    assert doc["trip_details"]["Place Name"] == "Kyoto"


async def test_start_ongoing_trip_without_saved_trip_is_empty(db):
    await ongoing_trip_service.start_ongoing_trip(db, "alice", "Atlantis")
    doc = await ongoing_trip_service.get_ongoing_trip(db, "alice")
    assert doc["trip_details"] == {}


async def test_add_expense_accumulates(db):
    first = await ongoing_trip_service.add_expense(db, "alice", "Kyoto", {"amount": 10, "category": "Food", "date": "01/01/2026"})
    assert first == [{"amount": 10, "category": "Food", "date": "01/01/2026"}]

    second = await ongoing_trip_service.add_expense(db, "alice", "Kyoto", {"amount": 5, "category": "Transport", "date": "01/02/2026"})
    assert len(second) == 2


async def test_end_ongoing_trip_removes_trip_and_itinerary(db):
    await ongoing_trip_service.start_ongoing_trip(db, "alice", "Kyoto")
    await db["itinerary"].insert_one({"username": "alice", "place": "Kyoto", "itinerary_by_date": {}})

    await ongoing_trip_service.end_ongoing_trip(db, "alice", "Kyoto")

    assert await ongoing_trip_service.get_ongoing_trip(db, "alice") is None
    assert await db["itinerary"].find_one({"username": "alice", "place": "Kyoto"}) is None
