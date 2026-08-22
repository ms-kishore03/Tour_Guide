import httpx
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.metrics import track_external_api_call
from app.schemas.flight import FlightOption

from Utilities.agents import get_airport_id  # noqa: E402


async def _get_flight_details(
    departure_id: str,
    arrival_id: str,
    outbound_date: str,
    return_date: str,
    currency: str,
    travel_class: int,
    trip_type: int,
    adults: int,
    children: int,
    infants_in_seat: int,
    infants_in_lap: int,
) -> list[dict]:
    """Async-native reimplementation of API_Handlers/FlightHandler_V2.py::get_flight_details.

    Legacy module (which uses the sync serpapi SDK) stays untouched for the
    Streamlit app; this is the FastAPI hot path, calling SerpApi's REST
    endpoint directly over httpx instead of run_in_threadpool.
    """
    params = {
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": currency,
        "travel_class": travel_class,
        "type": trip_type,
        "adults": adults,
        "children": children,
        "infants_in_seat": infants_in_seat,
        "infants_in_lap": infants_in_lap,
        "api_key": get_settings().serpapi_api_key,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get("https://serpapi.com/search.json", params=params)
        resp.raise_for_status()
        results = resp.json()

    seen = set()
    flight_options = []
    for flight in results.get("best_flights", []):
        if "flights" not in flight or not flight["flights"]:
            continue

        dep = flight["flights"][0]["departure_airport"]["time"]
        arr = flight["flights"][-1]["arrival_airport"]["time"]
        price = flight.get("price")

        flight_key = (dep, arr, price)
        if flight_key in seen:
            continue
        seen.add(flight_key)

        airlines = ", ".join({seg["airline"] for seg in flight["flights"]})

        total_minutes = flight["total_duration"]
        total_duration = f"{total_minutes // 60} hrs {total_minutes % 60} mins"

        layovers = len(flight.get("layovers", []))
        carbon_grams = flight.get("carbon_emissions", {}).get("this_flight", 0)
        carbon_emission = f"{carbon_grams / 1000:.1f} kg CO2e"

        flight_options.append(
            {
                "departure_time": dep,
                "arrival_time": arr,
                "airlines": airlines,
                "duration": total_duration,
                "layovers": layovers,
                "price": f"{price} {currency}" if price else "N/A",
                "carbon_emission": carbon_emission,
            }
        )
    return flight_options


async def search_flights(
    departure: str,
    arrival: str,
    outbound_date: str,
    return_date: str,
    currency: str,
    travel_class: int,
    trip_type: int,
    adults: int,
    children: int,
    infants_in_seat: int,
    infants_in_lap: int,
) -> list[FlightOption]:
    departure_id = await run_in_threadpool(get_airport_id, departure)
    arrival_id = await run_in_threadpool(get_airport_id, arrival)

    with track_external_api_call("serpapi"):
        records = await _get_flight_details(
            departure_id,
            arrival_id,
            outbound_date,
            return_date,
            currency,
            travel_class,
            trip_type,
            adults,
            children,
            infants_in_seat,
            infants_in_lap,
        )
    return [FlightOption(**r) for r in records]
