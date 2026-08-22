from app.services import flight_service, hotel_service


async def test_accommodations_search_route(client, monkeypatch):
    async def fake_search(location, checkin, checkout):
        return ["Hotel A"]

    monkeypatch.setattr(hotel_service, "_search_accommodations", fake_search)
    res = await client.post(
        "/api/v1/accommodations/search",
        json={"location": "Kyoto", "checkin": "2026-01-01", "checkout": "2026-01-05"},
    )
    assert res.status_code == 200
    assert res.json() == {"results": ["Hotel A"]}


async def test_flights_search_route(client, monkeypatch):
    async def fake_get_flight_details(*a, **kw):
        return [
            {
                "departure_time": "10:00",
                "arrival_time": "14:00",
                "airlines": "Test Air",
                "duration": "4 hrs 0 mins",
                "layovers": 0,
                "price": "500 USD",
                "carbon_emission": "1.2 kg CO2e",
            }
        ]

    monkeypatch.setattr(flight_service, "get_airport_id", lambda city: "XXX")
    monkeypatch.setattr(flight_service, "_get_flight_details", fake_get_flight_details)
    res = await client.post(
        "/api/v1/flights/search",
        json={
            "departure": "Tokyo",
            "arrival": "Paris",
            "outbound_date": "2026-01-01",
            "currency": "USD",
        },
    )
    assert res.status_code == 200
    assert len(res.json()["flights"]) == 1
