import pytest

from cognix_ai.brain.cognix import CognixAI


class FakeChunk:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, invoke_content: str = "TOOLS:\nNONE", stream_chunks: list[str] | None = None):
        self.invoke_content = invoke_content
        self.stream_chunks = stream_chunks or ["Hello ", "world"]

    def invoke(self, prompt: str):
        return FakeChunk(self.invoke_content)

    async def astream(self, prompt: str):
        for piece in self.stream_chunks:
            yield FakeChunk(piece)


def fake_weather_tool(query, context):
    return "sunny and 25C"


def fake_itinerary_tool(query, context):
    return "saved"


async def collect(agen):
    return [event async for event in agen]


@pytest.fixture
def tools():
    return {"WEATHER": fake_weather_tool, "ITINERARY": fake_itinerary_tool}


async def test_run_stream_weather_hard_route(tools):
    agent = CognixAI(tools, llm=FakeLLM())
    events = await collect(agent.run_stream("what's the weather like", {"place": "Kyoto"}))

    types = [e["type"] for e in events]
    assert types == ["tool_call", "tool_result", "final"]
    assert events[0]["tool"] == "WEATHER"
    assert events[-1]["data"]["message"] == "sunny and 25C"


async def test_run_stream_draft_edit(tools):
    agent = CognixAI(tools, llm=FakeLLM(invoke_content='{"draft_itinerary": [{"location": "Temple", "date": "unknown", "time": "unknown"}]}'))
    events = await collect(agent.run_stream("add a visit to the temple", {"place": "Kyoto", "draft_itinerary": []}))

    types = [e["type"] for e in events]
    assert types == ["tool_call", "final"]
    assert events[-1]["data"]["draft_itinerary"][0]["location"] == "Temple"
    assert "Kyoto" not in agent.memory  # sanity: memory holds user turns, not place
    assert agent.memory == ["add a visit to the temple"]


async def test_run_stream_fallback_streams_tokens(tools):
    agent = CognixAI(tools, llm=FakeLLM(stream_chunks=["Hi ", "there!"]))
    events = await collect(agent.run_stream("tell me something interesting", {"place": "Kyoto"}))

    token_events = [e for e in events if e["type"] == "token"]
    assert [e["data"] for e in token_events] == ["Hi ", "there!"]
    assert events[-1]["type"] == "final"
    assert events[-1]["data"]["message"] == "Hi there!"


async def test_run_stream_finalize(tools):
    agent = CognixAI(tools, llm=FakeLLM())
    context = {
        "place": "Kyoto",
        "draft_itinerary": [{"location": "Temple", "date": "01/01/2026", "time": "10:00 AM"}],
    }
    events = await collect(agent.run_stream("please finalize my plan", context))

    types = [e["type"] for e in events]
    assert types == ["tool_call", "tool_result", "final"]
    assert events[-1]["data"]["status"] == "finalized"
    assert "Day 1" in events[-1]["data"]["day_summary"]
