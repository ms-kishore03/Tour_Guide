import requests
import os,sys
from dotenv import load_dotenv
load_dotenv(".env")

api_key = os.getenv("GEOAPIFY_API_KEY")

def geoapify_attractions(place):
    url_1 = "https://api.geoapify.com/v1/geocode/search?text={}&format=json&apiKey={}".format(place, api_key)

    payload = {}
    headers = {}

    response = requests.request("GET", url_1, headers=headers, data=payload)
    lat = response.json()['results'][0]['lat']
    lon = response.json()['results'][0]['lon']

    url_2 = "https://api.geoapify.com/v2/places?categories=tourism.attraction,tourism.sights,tourism&filter=circle:{},{},5000&bias=proximity:{},{}&limit=30&apiKey={}".format(lon, lat, lon, lat, api_key)

    payload = {}
    headers = {}

    response = requests.request("GET", url_2, headers=headers, data=payload)

    attractions_list = []

    idx = 0
    for feature in response.json().get("features", []):
        props = feature.get("properties", {})

        name = props.get("name")
        address = props.get("formatted")

        if not name or not address:
            continue

        attraction = {
            "name": name,
            "city": props.get("city"),
            "postcode": props.get("postcode"),
            "address": address
        }

        attractions_list.append(attraction)
        idx += 1
    return attractions_list