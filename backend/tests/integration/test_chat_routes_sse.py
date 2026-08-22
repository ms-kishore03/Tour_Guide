import pytest

from app.core.security import create_access_token
from app.schemas.common import UserContext
from app.services import auth_service, chat_service


@pytest.fixture
def auth_headers():
    token = create_access_token("alice")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def patch_current_user(monkeypatch):
    async def fake_get_current_user(username):
        return UserContext(username=username, email="alice@example.com")

    monkeypatch.setattr(auth_service, "get_current_user", fake_get_current_user)


class FakeStreamAgent:
    def __init__(self, tools, memory=None, llm=None):
        self.memory = list(memory or [])

    async def run_stream(self, user_input, context):
        yield {"type": "tool_call", "tool": "WEATHER"}
        yield {"type": "token", "data": "It's "}
        yield {"type": "token", "data": "sunny."}
        yield {"type": "final", "data": {"message": "It's sunny."}}


@pytest.fixture(autouse=True)
def patch_agent(monkeypatch):
    monkeypatch.setattr(chat_service, "CognixAI", FakeStreamAgent)
    monkeypatch.setattr(chat_service, "get_llm", lambda: "fake-llm")
    monkeypatch.setattr(chat_service, "_itinerary_collection", lambda: _NullCollection())


class _NullCollection:
    def find_one(self, *a, **kw):
        return None


async def test_chat_stream_emits_well_formed_sse_frames_and_ends_with_final(client, auth_headers):
    res = await client.post(
        "/api/v1/chat/Kyoto/stream", json={"message": "what's the weather"}, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/event-stream")

    body = res.text
    frames = [f for f in body.split("\n\n") if f.strip()]
    assert len(frames) == 4
    assert frames[0].startswith("event: tool_call")
    assert frames[1].startswith("event: token")
    assert frames[-1].startswith("event: final")
    assert "It's sunny." in frames[-1]


async def test_chat_stream_requires_auth(client):
    res = await client.post("/api/v1/chat/Kyoto/stream", json={"message": "hi"})
    assert res.status_code == 401


async def test_chat_stream_persists_conversation(client, auth_headers, override_db):
    await client.post("/api/v1/chat/Kyoto/stream", json={"message": "what's the weather"}, headers=auth_headers)

    doc = await override_db["Conversations"].find_one({"username": "alice", "place": "Kyoto"})
    assert doc is not None
    assert doc["memory"] == ["what's the weather"]
    assert doc["messages"][-1]["content"] == "It's sunny."
    assert doc["messages"][-1]["partial"] is False
