import re

import httpx
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.metrics import track_external_api_call

import Utilities.agents as agents  # noqa: E402

BOOKING_HOST = "booking-com18.p.rapidapi.com"


async def _search_accommodations(location: str, checkin: str, checkout: str) -> list[str]:
    """Async-native reimplementation of API_Handlers/AccomodationHandler.py::get_accomodations.

    Legacy module stays sync/untouched for the Streamlit app; this is the
    FastAPI hot path, using httpx instead of requests + run_in_threadpool for
    the two Booking.com HTTP calls (LLM ranking below still runs via threadpool).
    """
    api_key = get_settings().accomodation_api_key
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": BOOKING_HOST}

    async with httpx.AsyncClient(timeout=15) as client:
        auto_resp = await client.get(
            f"https://{BOOKING_HOST}/stays/auto-complete",
            headers=headers,
            params={"query": location},
        )
        auto_resp.raise_for_status()
        loc_res = auto_resp.json()
        loc_id = loc_res["data"][0]["id"]

        search_resp = await client.get(
            f"https://{BOOKING_HOST}/stays/search",
            headers=headers,
            params={
                "locationId": loc_id,
                "checkinDate": checkin,
                "checkoutDate": checkout,
                "units": "metric",
                "temperature": "c",
            },
        )
        search_resp.raise_for_status()
        stay_res = search_resp.json()

    stays = stay_res.get("data", [])
    # skip index 0 (first result), take up to 10 more, bounded to what's actually returned
    upper = min(10, max(len(stays) - 1, 0))
    names = [stays[i]["name"] for i in range(upper, 0, -1)]

    accomodations_list = await run_in_threadpool(agents.retieve_hotel_names, location, names)
    lines = accomodations_list.splitlines()
    clean = []
    for line in lines:
        match = re.match(r"\d+\.\s*(.+)", line)
        if match:
            clean.append(match.group(1).strip())
    return clean


async def search_accommodations(location: str, checkin: str, checkout: str) -> list[str]:
    with track_external_api_call("booking"):
        return await _search_accommodations(location, checkin, checkout)
