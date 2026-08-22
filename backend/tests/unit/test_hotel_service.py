import httpx
import respx

from app.services import hotel_service
from API_Handlers import AccomodationHandler


async def test_search_accommodations_delegates_to_impl(monkeypatch):
    async def fake_search(location, checkin, checkout):
        return ["Hotel A", "Hotel B"]

    monkeypatch.setattr(hotel_service, "_search_accommodations", fake_search)
    results = await hotel_service.search_accommodations("Kyoto", "2026-01-01", "2026-01-05")
    assert results == ["Hotel A", "Hotel B"]


@respx.mock
async def test_search_accommodations_handles_fewer_than_eleven_results(monkeypatch):
    """Regression test for the crash bug: the old code did
    `for i in range(10, 0, -1): stay_res["data"][i]` with no bounds check,
    which raised IndexError whenever fewer than 11 stays were returned.
    Exercises the async httpx implementation directly."""
    respx.get(f"https://{hotel_service.BOOKING_HOST}/stays/auto-complete").mock(
        return_value=httpx.Response(200, json={"data": [{"id": "loc-1"}]})
    )
    respx.get(f"https://{hotel_service.BOOKING_HOST}/stays/search").mock(
        return_value=httpx.Response(200, json={"data": [{"name": f"Hotel {i}"} for i in range(5)]})
    )
    monkeypatch.setattr(
        hotel_service.agents,
        "retieve_hotel_names",
        lambda location, names: "\n".join(f"{i + 1}. {n}" for i, n in enumerate(names)),
    )

    result = await hotel_service._search_accommodations("Kyoto", "2026-01-01", "2026-01-05")
    assert len(result) == 4  # indices 4,3,2,1 (index 0 skipped, bounded to available data)


@respx.mock
async def test_search_accommodations_handles_zero_results(monkeypatch):
    respx.get(f"https://{hotel_service.BOOKING_HOST}/stays/auto-complete").mock(
        return_value=httpx.Response(200, json={"data": [{"id": "loc-1"}]})
    )
    respx.get(f"https://{hotel_service.BOOKING_HOST}/stays/search").mock(
        return_value=httpx.Response(200, json={"data": []})
    )
    monkeypatch.setattr(hotel_service.agents, "retieve_hotel_names", lambda location, names: "")

    result = await hotel_service._search_accommodations("Nowhere", "2026-01-01", "2026-01-05")
    assert result == []


def test_legacy_accomodation_handler_still_bounds_safe(monkeypatch):
    """Legacy sync module (used by Streamlit) keeps the same bug fix independently."""
    monkeypatch.setattr(
        AccomodationHandler, "get_location_autocomplete", lambda query: {"data": [{"id": "loc-1"}]}
    )
    monkeypatch.setattr(
        AccomodationHandler,
        "search_stays",
        lambda location_id, checkin, checkout: {
            "data": [{"name": f"Hotel {i}"} for i in range(5)]
        },
    )
    monkeypatch.setattr(AccomodationHandler.agents, "retieve_hotel_names", lambda location, names: "\n".join(
        f"{i+1}. {n}" for i, n in enumerate(names)
    ))

    result = AccomodationHandler.get_accomodations("Kyoto", "2026-01-01", "2026-01-05")
    assert len(result) == 4
