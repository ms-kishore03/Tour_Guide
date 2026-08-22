from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongo import ITINERARY, USER_PLANS


async def get_itinerary(db: AsyncIOMotorDatabase, username: str, place: str) -> dict:
    doc = await db[ITINERARY].find_one({"username": username, "place": place}, {"_id": 0, "itinerary_by_date": 1})
    if not doc:
        return {}
    return doc.get("itinerary_by_date", {})


async def get_todos(db: AsyncIOMotorDatabase, username: str, place: str) -> list[str]:
    user = await db[USER_PLANS].find_one({"username": username}, {"_id": 0})
    if not user:
        return []
    for plan in user.get("plans", []):
        if plan.get("place") == place:
            return [t.get("task") for t in plan.get("tasks", [])]
    return []


async def add_todo(db: AsyncIOMotorDatabase, username: str, place: str, task: str) -> list[str]:
    await db[USER_PLANS].update_one(
        {"username": username}, {"$setOnInsert": {"plans": []}}, upsert=True
    )

    result = await db[USER_PLANS].update_one(
        {"username": username, "plans.place": place},
        {"$push": {"plans.$.tasks": {"task": task}}},
    )

    if result.matched_count == 0:
        await db[USER_PLANS].update_one(
            {"username": username},
            {"$push": {"plans": {"place": place, "tasks": [{"task": task}]}}},
        )

    return await get_todos(db, username, place)
