import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key = os.getenv("GEOAPIFY_API_KEY")


def geoapify_attractions(place):
    """
    Safely fetch nearby attractions for a place.
    Returns an EMPTY LIST if geocoding or places lookup fails.
    """

    try:
        # ----------------- STEP 1: GEOCODE -----------------
        url_1 = (
            "https://api.geoapify.com/v1/geocode/search"
            f"?text={place}&format=json&apiKey={api_key}"
        )

        response = requests.get(url_1, timeout=10)
        response.raise_for_status()

        results = response.json().get("results", [])

        # 🚨 SAFETY CHECK
        if not results:
            return []

        lat = results[0].get("lat")
        lon = results[0].get("lon")

        if lat is None or lon is None:
            return []

        # ----------------- STEP 2: FETCH ATTRACTIONS -----------------
        url_2 = (
            "https://api.geoapify.com/v2/places"
            "?categories=tourism.attraction,tourism.sights,tourism"
            f"&filter=circle:{lon},{lat},5000"
            f"&bias=proximity:{lon},{lat}"
            f"&limit=30&apiKey={api_key}"
        )

        response = requests.get(url_2, timeout=10)
        response.raise_for_status()

        attractions_list = []

        for feature in response.json().get("features", []):
            props = feature.get("properties", {})

            name = props.get("name")
            address = props.get("formatted")

            if not name:
                continue

            attraction = {
                "name": name,
                "city": props.get("city"),
                "postcode": props.get("postcode"),
                "address": address,
            }

            attractions_list.append(attraction)

        return attractions_list

    except Exception:
        # 🚨 NEVER crash the app
        return []
