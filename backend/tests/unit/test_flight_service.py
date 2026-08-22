import pytest

from app.services import flight_service


@pytest.fixture(autouse=True)
def patch_airport_lookup(monkeypatch):
    monkeypatch.setattr(flight_service, "get_airport_id", lambda city: f"{city[:3].upper()}X")


async def test_search_flights_resolves_airport_names_and_maps_records(monkeypatch):
    captured = {}

    async def fake_get_flight_details(departure_id, arrival_id, *args, **kwargs):
        captured["departure_id"] = departure_id
        captured["arrival_id"] = arrival_id
        return [
            {
                "departure_time": "2026-01-01 10:00",
                "arrival_time": "2026-01-01 14:00",
                "airlines": "Test Air",
                "duration": "4 hrs 0 mins",
                "layovers": 0,
                "price": "500 USD",
                "carbon_emission": "1.2 kg CO2e",
            }
        ]

    monkeypatch.setattr(flight_service, "_get_flight_details", fake_get_flight_details)

    flights = await flight_service.search_flights(
        "Tokyo", "Paris", "2026-01-01", "2026-01-10", "USD", 1, 1, 1, 0, 0, 0
    )

    assert captured["departure_id"] == "TOKX"
    assert captured["arrival_id"] == "PARX"
    assert len(flights) == 1
    assert flights[0].airlines == "Test Air"


async def test_search_flights_returns_empty_list_for_no_results(monkeypatch):
    async def fake_get_flight_details(*a, **kw):
        return []

    monkeypatch.setattr(flight_service, "_get_flight_details", fake_get_flight_details)

    flights = await flight_service.search_flights(
        "Nowhere", "Nowhere Else", "2026-01-01", "", "USD", 1, 1, 1, 0, 0, 0
    )
    assert flights == []
