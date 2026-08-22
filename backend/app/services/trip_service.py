from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.db.mongo import PLANNING_TRIPS, SAVED_TRIPS
from app.schemas.trip import ExploreSuggestion, TripResponse

from Utilities.explore import suggest_places as legacy_suggest_places  # noqa: E402


async def suggest_places(
    trip_theme: str,
    activity: str,
    climate: str,
    budget: str,
    duration: str,
    location: str,
    trip_type: str,
    transport: str,
) -> list[ExploreSuggestion]:
    places, descriptions = await run_in_threadpool(
        legacy_suggest_places,
        trip_theme,
        activity,
        climate,
        budget,
        duration,
        location,
        trip_type,
        transport,
    )
    return [ExploreSuggestion(name=p, description=d) for p, d in zip(places, descriptions)]


async def save_trip(db: AsyncIOMotorDatabase, username: str, trip: dict) -> str:
    """Returns 'exists' or 'saved'."""
    match = await db[SAVED_TRIPS].find_one({"username": username, "trip_data": trip})
    if match:
        return "exists"
    await db[SAVED_TRIPS].insert_one({"username": username, "trip_data": trip})
    return "saved"


async def get_saved_trips(db: AsyncIOMotorDatabase, username: str) -> list[TripResponse]:
    cursor = db[SAVED_TRIPS].find({"username": username})
    trips = [doc["trip_data"] async for doc in cursor if "trip_data" in doc]
    return [TripResponse.from_legacy_dict(t) for t in trips]


async def get_saved_trip(db: AsyncIOMotorDatabase, username: str, place_name: str) -> TripResponse | None:
    doc = await db[SAVED_TRIPS].find_one({"username": username, "trip_data.Place Name": place_name})
    if not doc:
        return None
    return TripResponse.from_legacy_dict(doc["trip_data"])


async def delete_saved_trip(db: AsyncIOMotorDatabase, username: str, place_name: str) -> bool:
    result = await db[SAVED_TRIPS].delete_one({"username": username, "trip_data.Place Name": place_name})
    return result.deleted_count > 0


async def start_planning(db: AsyncIOMotorDatabase, username: str, place_name: str) -> bool:
    trip = await get_saved_trip(db, username, place_name)
    if trip is None:
        return False
    trip_data = trip.model_dump()
    legacy_trip = {
        "Place Name": trip_data["place_name"],
        "Scenario": trip_data["scenario"],
        "Climate": trip_data["climate"],
        "Duration": trip_data["duration"],
        "People": trip_data["people"],
        "Transport": trip_data["transport"],
        "Description": trip_data["description"],
    }
    match = await db[PLANNING_TRIPS].find_one({"username": username, "trip_data": legacy_trip})
    if not match:
        await db[PLANNING_TRIPS].insert_one({"username": username, "trip_data": legacy_trip})
    return True
