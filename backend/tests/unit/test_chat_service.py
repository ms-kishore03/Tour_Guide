import pytest
from mongomock_motor import AsyncMongoMockClient

from app.services import chat_service


@pytest.fixture
def db():
    return AsyncMongoMockClient()["Tour_Guide_Test"]


class FakeAgent:
    def __init__(self, tools, memory=None, llm=None):
        self.tools = tools
        self.memory = list(memory or [])
        self.llm = llm
        self.last_input = None
        self.last_context = None

    def run(self, user_input, context):
        self.last_input = user_input
        self.last_context = context
        return {"message": f"echo: {user_input}"}


class FakeItineraryCollection:
    def find_one(self, *args, **kwargs):
        return None

    def update_one(self, *args, **kwargs):
        return None


@pytest.fixture(autouse=True)
def patch_agent(monkeypatch):
    monkeypatch.setattr(chat_service, "CognixAI", FakeAgent)
    monkeypatch.setattr(chat_service, "get_llm", lambda: "fake-llm")
    monkeypatch.setattr(
        chat_service, "_itinerary_collection", lambda: FakeItineraryCollection()
    )


async def test_run_chat_persists_memory_and_messages(db):
    response = await chat_service.run_chat(db, "alice", "Kyoto", "hello", None, None, None)
    assert response.message == "echo: hello"

    session = await db["Conversations"].find_one({"username": "alice", "place": "Kyoto"})
    assert session["memory"] == ["hello"]
    assert [m["role"] for m in session["messages"]] == ["user", "assistant"]
    assert session["messages"][0]["content"] == "hello"
    assert session["messages"][1]["content"] == "echo: hello"


async def test_run_chat_accumulates_memory_across_turns(db):
    await chat_service.run_chat(db, "alice", "Kyoto", "first", None, None, None)
    await chat_service.run_chat(db, "alice", "Kyoto", "second", None, None, None)

    session = await db["Conversations"].find_one({"username": "alice", "place": "Kyoto"})
    assert session["memory"] == ["first", "second"]
    assert len(session["messages"]) == 4


async def test_get_history_returns_persisted_messages(db):
    await chat_service.run_chat(db, "alice", "Kyoto", "hi", None, None, None)
    history = await chat_service.get_history(db, "alice", "Kyoto")
    assert len(history) == 2
    assert history[0]["role"] == "user"


async def test_run_chat_updates_draft_itinerary_from_result(db, monkeypatch):
    class DraftAgent(FakeAgent):
        def run(self, user_input, context):
            return {
                "draft_itinerary": [{"location": "Fushimi Inari", "date": "unknown", "time": "unknown"}],
                "message": "Got it.",
            }

    monkeypatch.setattr(chat_service, "CognixAI", DraftAgent)

    await chat_service.run_chat(db, "alice", "Kyoto", "visit Fushimi Inari", None, None, None)
    session = await db["Conversations"].find_one({"username": "alice", "place": "Kyoto"})
    assert session["draft_itinerary"] == [{"location": "Fushimi Inari", "date": "unknown", "time": "unknown"}]
