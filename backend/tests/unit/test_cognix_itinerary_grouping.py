from datetime import datetime

from cognix_ai.brain.cognix import CognixAI


def make_agent():
    return CognixAI(tools={}, llm=object())


def test_normalize_defaults_missing_date_to_today():
    agent = make_agent()
    today = datetime.today().strftime("%m/%d/%Y")
    itinerary = [{"location": "Temple", "date": "unknown", "time": "10:00 AM"}]
    normalized = agent._normalize_and_sort_itinerary(itinerary)
    assert normalized[0]["date"] == today


def test_normalize_defaults_missing_time_to_unknown():
    agent = make_agent()
    itinerary = [{"location": "Temple", "date": "01/01/2026", "time": ""}]
    normalized = agent._normalize_and_sort_itinerary(itinerary)
    assert normalized[0]["time"] == "unknown"


def test_normalize_sorts_unknown_time_first():
    agent = make_agent()
    itinerary = [
        {"location": "Shrine", "date": "01/01/2026", "time": "02:00 PM"},
        {"location": "Temple", "date": "01/01/2026", "time": "unknown"},
    ]
    normalized = agent._normalize_and_sort_itinerary(itinerary)
    assert [item["location"] for item in normalized] == ["Temple", "Shrine"]


def test_group_by_day_keeps_every_item_per_day():
    """Regression test guarding against the old Streamlit rendering bug where
    only the last item of each day was ever displayed — the grouping logic
    itself must retain every item."""
    agent = make_agent()
    itinerary = [
        {"location": "Fushimi Inari", "date": "01/01/2026", "time": "09:00 AM"},
        {"location": "Kiyomizu-dera", "date": "01/01/2026", "time": "01:00 PM"},
        {"location": "Gion District", "date": "01/01/2026", "time": "06:00 PM"},
        {"location": "Arashiyama", "date": "01/02/2026", "time": "10:00 AM"},
    ]
    grouped = agent._group_itinerary_by_day(itinerary)
    assert len(grouped["Day 1"]) == 3
    assert len(grouped["Day 2"]) == 1
    assert [i["location"] for i in grouped["Day 1"]] == [
        "Fushimi Inari",
        "Kiyomizu-dera",
        "Gion District",
    ]
