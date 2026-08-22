from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongo_db_name]


def close_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


# collection name constants (mirrors legacy Utilities/databaseManager.py)
USERS = "Users_Database"
PLACES = "Places_Database"
THINGS_TO_DO = "Things_To_Do"
SAVED_TRIPS = "Saved_Trips"
PLANNING_TRIPS = "Planning_Trips"
USER_PLANS = "User_Plans"
ITINERARY = "itinerary"
ONGOING_TRIPS = "Ongoing_Trips"
CONVERSATIONS = "Conversations"
REFRESH_TOKENS = "RefreshTokens"
