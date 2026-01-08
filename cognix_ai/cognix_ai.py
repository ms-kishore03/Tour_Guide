# cognix_ai.py

from typing import Optional, List
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cognix_ai.brain.cognix import CognixAI
from cognix_ai.tools.itinerary_tool import Itinerary_Agent
from cognix_ai.tools.attractions_tool import select_top_attractions
from cognix_ai.tools.Weather_tool import Weather_Explainer_Agent
from cognix_ai.tools.hotel_tool import retieve_hotel_names
from cognix_ai.tools.rag_tool import rag_tool
from config.settings import mongo_db_client as client


# ---------------- DATABASE ----------------
db = client["Tour_Guide"]
collection = db["itinerary"]

# ---------------- SESSION MEMORY ----------------
SESSION_STATE = {}


# ============================================================
# INTERNAL: Load itinerary from DB (SOURCE OF TRUTH)
# ============================================================
def _load_itinerary_from_db(username: str, place: Optional[str]) -> list:
    if not place:
        return []

    doc = collection.find_one(
        {"username": username, "place": place},
        {"_id": 0, "itinerary_list": 1}
    )

    if doc and isinstance(doc.get("itinerary_list"), list):
        return doc["itinerary_list"]

    return []


# ============================================================
# MAIN AGENT ENTRY
# ============================================================
def cognix_ai(
    user_input: str,
    username: str,
    place: Optional[str] = None,
    hotel_names: Optional[list] = None,
    weather_data: Optional[list] = None,
    conversation_history: Optional[list] = None,
    geoapify_data: Optional[list] = None,
):
    """
    Conversational agent (chat + planning).

    Returns:
    - str  -> normal chat
    - dict -> draft / finalized itinerary
    """

    # ---------------- INIT USER SESSION ----------------
    if username not in SESSION_STATE:
        SESSION_STATE[username] = {
            "draft_itinerary": [],
            "memory": []
        }

    # ---------------- HYDRATE DRAFT FROM DB ----------------
    if not SESSION_STATE[username]["draft_itinerary"] and place:
        SESSION_STATE[username]["draft_itinerary"] = _load_itinerary_from_db(
            username, place
        )

    # ---------------- TOOLS ----------------
    tools = {
        "ITINERARY": Itinerary_Agent,
        "ATTRACTIONS": select_top_attractions,
        "WEATHER": Weather_Explainer_Agent,
        "HOTEL": retieve_hotel_names,
        "RAG": rag_tool,
    }

    agent = CognixAI(
        tools=tools,
        memory=SESSION_STATE[username]["memory"]
    )

    # ---------------- CONTEXT ----------------
    context = {
        "username": username,
        "place": place,
        "draft_itinerary": SESSION_STATE[username]["draft_itinerary"],
        "collection": collection,
        "llm": agent.llm,
    }

    if hotel_names:
        context["hotel_names"] = hotel_names
    if weather_data:
        context["weather_data"] = weather_data
    if geoapify_data:
        context["geoapify_data"] = geoapify_data
    if conversation_history:
        context["conversation_history"] = conversation_history

    # ---------------- RUN AGENT ----------------
    result = agent.run(user_input, context)

    # ---------------- MEMORY UPDATE ----------------
    SESSION_STATE[username]["memory"].append(user_input)

    # ---------------- DRAFT SYNC ----------------
    if isinstance(result, dict):
        if "draft_itinerary" in result:
            SESSION_STATE[username]["draft_itinerary"] = result["draft_itinerary"]
        elif result.get("status") == "finalized":
            # after finalize, DB is truth
            SESSION_STATE[username]["draft_itinerary"] = result.get("itinerary", [])

    return result


# ============================================================
# UI-SAFE ATTRACTION FETCHER (NO STRING BUG)
# ============================================================
def get_top_attractions_for_ui(
    *,
    place: str,
    geoapify_data: list,
    llm
) -> List[str]:
    """
    ALWAYS returns list[str]
    NEVER returns text / dict
    """

    attractions = select_top_attractions(
        query="top attractions",
        context={
            "place": place,
            "geoapify_data": geoapify_data,
            "llm": llm
        }
    )

    if not isinstance(attractions, list):
        return []

    return attractions[:10]
