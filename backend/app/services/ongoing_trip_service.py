from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import ITINERARY, ONGOING_TRIPS
from app.services.trip_service import get_saved_trip


async def start_ongoing_trip(db: AsyncIOMotorDatabase, username: str, place: str) -> None:
    trip = await get_saved_trip(db, username, place)
    if trip is not None:
        trip_details = {
            "Place Name": trip.place_name,
            "Scenario": trip.scenario,
            "Climate": trip.climate,
            "Duration": trip.duration,
            "People": trip.people,
            "Transport": trip.transport,
            "Description": trip.description,
        }
    else:
        trip_details = {}

    await db[ONGOING_TRIPS].update_one(
        {"username": username, "place": place},
        {"$set": {"username": username, "place": place, "trip_details": trip_details}},
        upsert=True,
    )


async def get_ongoing_trip(db: AsyncIOMotorDatabase, username: str) -> dict | None:
    return await db[ONGOING_TRIPS].find_one({"username": username}, {"_id": 0})


async def save_expenses(db: AsyncIOMotorDatabase, username: str, place: str, expenses: list[dict]) -> None:
    await db[ONGOING_TRIPS].update_one(
        {"username": username, "place": place},
        {"$set": {"username": username, "place": place, "expenses": expenses}},
        upsert=True,
    )


async def get_expenses(db: AsyncIOMotorDatabase, username: str, place: str) -> list[dict]:
    doc = await db[ONGOING_TRIPS].find_one({"username": username, "place": place}, {"_id": 0, "expenses": 1})
    return doc.get("expenses", []) if doc else []


async def add_expense(db: AsyncIOMotorDatabase, username: str, place: str, expense: dict) -> list[dict]:
    expenses = await get_expenses(db, username, place)
    expenses.append(expense)
    await save_expenses(db, username, place, expenses)
    return expenses


async def end_ongoing_trip(db: AsyncIOMotorDatabase, username: str, place: str) -> None:
    await db[ONGOING_TRIPS].delete_one({"username": username, "place": place})
    await db[ITINERARY].delete_one({"username": username, "place": place})
