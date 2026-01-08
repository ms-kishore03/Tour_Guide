import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key = os.getenv("GEOAPIFY_API_KEY")


def geoapify_attractions(place):
    url_1 = (
        "https://api.geoapify.com/v1/geocode/search"
        f"?text={place}&format=json&apiKey={api_key}"
    )

    response = requests.get(url_1)
    geo_data = response.json()

    # ✅ HARD SAFETY CHECK
    if not geo_data.get("results"):
        print(f"[Geoapify] No geocoding results for: {place}")
        return []

    lat = geo_data["results"][0]["lat"]
    lon = geo_data["results"][0]["lon"]

    url_2 = (
        "https://api.geoapify.com/v2/places"
        f"?categories=tourism.attraction,tourism.sights"
        f"&filter=circle:{lon},{lat},5000"
        f"&limit=30"
        f"&apiKey={api_key}"
    )

    response = requests.get(url_2)
    places = response.json().get("features", [])

    attractions = []
    for f in places:
        name = f.get("properties", {}).get("name")
        if name:
            attractions.append(name)

    return attractions