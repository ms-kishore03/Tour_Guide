# cognix_ai.py

from cognix_ai.brain.cognix import CognixAI
from cognix_ai.tools.itinerary_tool import Itinerary_Agent
from cognix_ai.tools.attractions_tool import select_top_attractions
from cognix_ai.tools.Weather_tool import Weather_Explainer_Agent
from cognix_ai.tools.hotel_tool import retieve_hotel_names
from cognix_ai.tools.rag_tool import rag_tool

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.settings import mongo_db_client as client
from typing import Optional, List

# ---------------- DATABASE ----------------
db = client["Tour_Guide"]
collection = db["itinerary"]

# ---------------- PLACE-SCOPED SESSION MEMORY ----------------
SESSION_STATE = {}


def _load_itinerary_from_db(username: str, place: str) -> list:
    """
    Load finalized itinerary from DB (authoritative).
    """
    doc = collection.find_one({
        "username": username,
        "place": place
    })

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
    conversation_history: Optional[list] = None,  # UI only
    geoapify_data: Optional[list] = None,
):
    # ---------------- SAFETY ----------------
    if not place:
        place = "__global__"

    # ---------------- SESSION INIT ----------------
    if username not in SESSION_STATE:
        SESSION_STATE[username] = {}

    if place not in SESSION_STATE[username]:
        SESSION_STATE[username][place] = {
            "memory": [],
            "draft_itinerary": _load_itinerary_from_db(username, place)
        }

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
        memory=SESSION_STATE[username][place]["memory"]
    )

    # ---------------- CONTEXT ----------------
    context = {
        "username": username,
        "place": place,
        "draft_itinerary": SESSION_STATE[username][place]["draft_itinerary"],
        "collection": collection,
        "llm": agent.llm
    }

    # Optional context enrichment
    if weather_data is not None:
        context["weather_data"] = weather_data

    if geoapify_data is not None:
        context["geoapify_data"] = geoapify_data

    if conversation_history:
        context["conversation_history"] = conversation_history

    # ---------------- RUN AGENT ----------------
    result = agent.run(user_input, context)

    # ---------------- MEMORY PERSIST ----------------
    SESSION_STATE[username][place]["memory"].append(user_input)

    # ---------------- DRAFT UPDATE ----------------
    if isinstance(result, dict) and "draft_itinerary" in result:
        SESSION_STATE[username][place]["draft_itinerary"] = result["draft_itinerary"]

    # ---------------- FINALIZE → SYNC DB FOR FUTURE ----------------
    if isinstance(result, dict) and result.get("status") == "finalized":
        SESSION_STATE[username][place]["draft_itinerary"] = _load_itinerary_from_db(
            username, place
        )

    return result


# ============================================================
# UI-SAFE ATTRACTION HELPER
# ============================================================
def get_top_attractions_for_ui(
    *,
    place: str,
    geoapify_data: list,
    llm
) -> List[str]:
    """
    UI helper — always returns list[str].
    """
    attractions = select_top_attractions(
        query="top attractions",
        context={
            "place": place,
            "geoapify_data": geoapify_data,
            "llm": llm
        }
    )

    return attractions[:10] if isinstance(attractions, list) else []
