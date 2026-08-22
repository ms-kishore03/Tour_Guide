import json
import time
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, AsyncIterator, Callable

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import MongoClient
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.llm import get_llm
from app.core.metrics import (
    agent_tool_invocations_total,
    chat_streaming_session_duration_seconds,
    chat_streaming_sessions_active,
    track_llm_call,
)
from app.db.mongo import CONVERSATIONS, ITINERARY
from app.schemas.chat import ChatResponse

from cognix_ai.brain.cognix import CognixAI  # noqa: E402
from cognix_ai.tools.attractions_tool import select_top_attractions  # noqa: E402
from cognix_ai.tools.hotel_tool import retieve_hotel_names  # noqa: E402
from cognix_ai.tools.itinerary_tool import Itinerary_Agent  # noqa: E402
from cognix_ai.tools.rag_tool import rag_tool  # noqa: E402
from cognix_ai.tools.Weather_tool import Weather_Explainer_Agent  # noqa: E402


@lru_cache
def _legacy_sync_mongo() -> MongoClient:
    """A small secondary sync pymongo client, used only inside tool execution
    (itinerary_tool.Itinerary_Agent does a sync collection.update_one). Kept
    separate from the Motor client used for everything else in the backend."""
    return MongoClient(get_settings().mongodb_uri)


def _itinerary_collection():
    return _legacy_sync_mongo()[get_settings().mongo_db_name][ITINERARY]


def build_tools() -> dict:
    return {
        "ITINERARY": Itinerary_Agent,
        "ATTRACTIONS": select_top_attractions,
        "WEATHER": Weather_Explainer_Agent,
        "HOTEL": retieve_hotel_names,
        "RAG": rag_tool,
    }


async def get_or_create_session(db: AsyncIOMotorDatabase, username: str, place: str) -> dict:
    doc = await db[CONVERSATIONS].find_one({"username": username, "place": place})
    if doc:
        return doc

    draft_itinerary: list = []
    itinerary_doc = await run_in_threadpool(
        lambda: _itinerary_collection().find_one({"username": username, "place": place})
    )
    if itinerary_doc:
        for date, items in itinerary_doc.get("itinerary_by_date", {}).items():
            for item in items:
                draft_itinerary.append({"location": item["location"], "date": date, "time": item["time"]})

    doc = {
        "username": username,
        "place": place,
        "memory": [],
        "messages": [],
        "draft_itinerary": draft_itinerary,
        "updated_at": datetime.now(timezone.utc),
    }
    await db[CONVERSATIONS].insert_one(doc)
    return doc


async def get_history(db: AsyncIOMotorDatabase, username: str, place: str) -> list[dict]:
    doc = await get_or_create_session(db, username, place)
    return doc.get("messages", [])


def _build_context(
    username: str,
    place: str,
    draft_itinerary: list,
    weather_data: str | None,
    geoapify_data: list[str] | None,
    rag_fn: Callable[[str], str] | None,
) -> dict:
    return {
        "username": username,
        "place": place,
        "draft_itinerary": draft_itinerary,
        "collection": _itinerary_collection(),
        "llm": get_llm(),
        "weather_data": weather_data,
        "geoapify_data": geoapify_data,
        "rag_fn": rag_fn,
    }


async def _persist_turn(
    db: AsyncIOMotorDatabase,
    username: str,
    place: str,
    session: dict,
    memory: list[str],
    user_message: str,
    assistant_message: str,
    draft_itinerary: list,
    partial: bool = False,
) -> None:
    now = datetime.now(timezone.utc)
    base_messages = session.get("messages", [])
    # replace a trailing partial assistant turn instead of appending a duplicate
    if base_messages and base_messages[-1].get("partial"):
        base_messages = base_messages[:-2]

    new_messages = base_messages + [
        {"role": "user", "content": user_message, "ts": now, "partial": False},
        {"role": "assistant", "content": assistant_message, "ts": now, "partial": partial},
    ]

    await db[CONVERSATIONS].update_one(
        {"username": username, "place": place},
        {
            "$set": {
                "memory": memory,
                "messages": new_messages,
                "draft_itinerary": draft_itinerary,
                "updated_at": now,
            }
        },
    )
    session["messages"] = new_messages


async def run_chat(
    db: AsyncIOMotorDatabase,
    username: str,
    place: str,
    message: str,
    weather_data: str | None,
    geoapify_data: list[str] | None,
    rag_fn: Callable[[str], str] | None,
) -> ChatResponse:
    session = await get_or_create_session(db, username, place)
    context = _build_context(username, place, session.get("draft_itinerary", []), weather_data, geoapify_data, rag_fn)

    agent = CognixAI(build_tools(), memory=list(session.get("memory", [])), llm=get_llm())
    with track_llm_call("chat_synthesis"):
        result = await run_in_threadpool(agent.run, message, context)

    # mirrors the legacy cognix_ai() wrapper: unconditionally record the turn,
    # regardless of which branch of agent.run() handled it
    agent.memory.append(message)

    if isinstance(result, dict):
        response = ChatResponse(
            message=result.get("message", ""),
            draft_itinerary=result.get("draft_itinerary") or result.get("itinerary") or context["draft_itinerary"],
            status=result.get("status"),
            day_summary=result.get("day_summary"),
        )
        new_draft_itinerary = response.draft_itinerary
    else:
        response = ChatResponse(message=str(result))
        new_draft_itinerary = context["draft_itinerary"]

    await _persist_turn(db, username, place, session, agent.memory, message, response.message, new_draft_itinerary)

    return response


def _sse_frame(event: str, data: Any, event_id: int) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\nid: {event_id}\n\n"


async def run_chat_stream(
    db: AsyncIOMotorDatabase,
    username: str,
    place: str,
    message: str,
    weather_data: str | None,
    geoapify_data: list[str] | None,
    rag_fn: Callable[[str], str] | None,
) -> AsyncIterator[str]:
    session = await get_or_create_session(db, username, place)
    context = _build_context(username, place, session.get("draft_itinerary", []), weather_data, geoapify_data, rag_fn)
    agent = CognixAI(build_tools(), memory=list(session.get("memory", [])), llm=get_llm())

    event_id = 0
    accumulated_text = ""
    last_persist_len = 0
    final_payload: dict = {}

    chat_streaming_sessions_active.inc()
    stream_start = time.perf_counter()

    try:
        async for event in agent.run_stream(message, context):
            event_id += 1
            yield _sse_frame(event["type"], event, event_id)

            if event["type"] == "tool_call" and event.get("tool"):
                agent_tool_invocations_total.labels(tool=event["tool"]).inc()

            if event["type"] == "token":
                accumulated_text += event["data"]
                # persist partial progress roughly every 40 characters so a
                # dropped connection can resume via GET /chat/{place}/history
                if len(accumulated_text) - last_persist_len >= 40:
                    last_persist_len = len(accumulated_text)
                    await _persist_turn(
                        db, username, place, session, agent.memory + [message], message, accumulated_text,
                        context["draft_itinerary"], partial=True,
                    )
            elif event["type"] == "final":
                final_payload = event["data"]
    except Exception as exc:  # pragma: no cover - defensive, surfaces as an SSE error frame
        event_id += 1
        yield _sse_frame("error", {"type": "error", "message": str(exc)}, event_id)
        return
    finally:
        chat_streaming_sessions_active.dec()
        chat_streaming_session_duration_seconds.observe(time.perf_counter() - stream_start)

    agent.memory.append(message)
    final_message = final_payload.get("message", accumulated_text)
    new_draft_itinerary = (
        final_payload.get("draft_itinerary") or final_payload.get("itinerary") or context["draft_itinerary"]
    )

    await _persist_turn(db, username, place, session, agent.memory, message, final_message, new_draft_itinerary)
