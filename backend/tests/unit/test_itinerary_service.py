import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from app.services import itinerary_service

# mongomock's positional `$` operator has a known bug (raises WriteError on a
# perfectly valid query/update pair that real MongoDB accepts), so these tests
# run against the real dev Mongo instance instead, with cleanup afterward.


@pytest.fixture
async def db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client["Tour_Guide_Test"]
    yield database
    await database["itinerary"].delete_many({"username": "alice"})
    await database["User_Plans"].delete_many({"username": "alice"})
    client.close()


async def test_get_itinerary_returns_all_items_per_day(db):
    """Regression test: the old Streamlit UI had a rendering bug where an
    inner loop overwrote `location`/`time` before display, so only the last
    item per day ever showed. The API must return every item for every day."""
    await db["itinerary"].insert_one(
        {
            "username": "alice",
            "place": "Kyoto",
            "itinerary_by_date": {
                "01/01/2026": [
                    {"location": "Fushimi Inari", "time": "09:00 AM"},
                    {"location": "Kiyomizu-dera", "time": "01:00 PM"},
                    {"location": "Gion District", "time": "06:00 PM"},
                ]
            },
        }
    )

    result = await itinerary_service.get_itinerary(db, "alice", "Kyoto")
    assert len(result["01/01/2026"]) == 3
    locations = [item["location"] for item in result["01/01/2026"]]
    assert locations == ["Fushimi Inari", "Kiyomizu-dera", "Gion District"]


async def test_get_itinerary_missing_returns_empty(db):
    result = await itinerary_service.get_itinerary(db, "alice", "Nowhere")
    assert result == {}


async def test_add_todo_creates_plan_for_new_place(db):
    todos = await itinerary_service.add_todo(db, "alice", "Kyoto", "Buy JR pass")
    assert todos == ["Buy JR pass"]


async def test_add_todo_appends_to_existing_place(db):
    await itinerary_service.add_todo(db, "alice", "Kyoto", "Buy JR pass")
    todos = await itinerary_service.add_todo(db, "alice", "Kyoto", "Book ryokan")
    assert todos == ["Buy JR pass", "Book ryokan"]


async def test_get_todos_scoped_by_place(db):
    await itinerary_service.add_todo(db, "alice", "Kyoto", "Buy JR pass")
    await itinerary_service.add_todo(db, "alice", "Osaka", "Try takoyaki")

    assert await itinerary_service.get_todos(db, "alice", "Kyoto") == ["Buy JR pass"]
    assert await itinerary_service.get_todos(db, "alice", "Osaka") == ["Try takoyaki"]
