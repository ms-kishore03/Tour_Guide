import httpx
import respx

from app.services import weather_service


async def test_get_weather_uses_provided_coordinates(monkeypatch):
    async def fake_weather_report(lat, lon, place):
        return "current-text", [{"a": 1}]

    monkeypatch.setattr(weather_service, "_weather_report", fake_weather_report)
    monkeypatch.setattr(weather_service, "Weather_Explainer_Agent", lambda query, context: "explanation-text")

    called_geocode = {"used": False}

    def fake_geocode(place):
        called_geocode["used"] = True
        return None, None

    monkeypatch.setattr(weather_service, "_geocode_sync", fake_geocode)

    res = await weather_service.get_weather("Kyoto", lat=35.0, lon=135.7)
    assert called_geocode["used"] is False
    assert res.explanation == "explanation-text"
    assert res.current == "current-text"
    assert res.forecast == [{"a": 1}]


async def test_get_weather_falls_back_to_geocoding_when_no_coords(monkeypatch):
    async def fake_weather_report(lat, lon, place):
        return "current-text", []

    monkeypatch.setattr(weather_service, "_geocode_sync", lambda place: (35.0, 135.7))
    monkeypatch.setattr(weather_service, "_weather_report", fake_weather_report)
    monkeypatch.setattr(weather_service, "Weather_Explainer_Agent", lambda query, context: "explanation-text")

    res = await weather_service.get_weather("Kyoto")
    assert res.current == "current-text"


@respx.mock
async def test_weather_report_calls_openweathermap_over_httpx():
    respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
        return_value=httpx.Response(
            200,
            json={
                "weather": [{"description": "clear sky"}],
                "main": {"temp": 300, "humidity": 40, "temp_max": 301, "temp_min": 299},
            },
        )
    )
    respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
        return_value=httpx.Response(
            200,
            json={
                "list": [
                    {
                        "dt_txt": "2026-01-01 12:00:00",
                        "main": {"temp": 300, "humidity": 40},
                        "weather": [{"description": "clear sky"}],
                    }
                ]
            },
        )
    )

    current, forecast = await weather_service._weather_report(35.0, 135.7, "Kyoto")
    assert "clear sky" in current
    assert forecast[0]["temperature"] == 300
