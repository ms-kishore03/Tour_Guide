import requests
import json
import agents
import re
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
API_Key = os.getenv("Accomodation_API_KEY")

def get_location_autocomplete(query):
    url = "https://booking-com18.p.rapidapi.com/stays/auto-complete"

    querystring = {
        "query": query
    }

    headers = {
        "x-rapidapi-key": API_Key,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    # Raise error if request fails
    response.raise_for_status()

    return response.json()

def search_stays(location_id, checkin, checkout):
    url = "https://booking-com18.p.rapidapi.com/stays/search"

    querystring = {
        "locationId": location_id,
        "checkinDate": checkin,
        "checkoutDate": checkout,
        "units": "metric",
        "temperature": "c"
    }

    headers = {
        "x-rapidapi-key": API_Key,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    return response.json()

def get_accomodations(location,checkin,checkout):
    loc_res = get_location_autocomplete(location)
    loc_id = loc_res["data"][0]["id"]
    stay_res = search_stays(loc_id, checkin, checkout)

    names = []
    for i in range(10,0,-1):
        hotel_name = stay_res["data"][i]["name"]
        names.append(hotel_name)
    
    accomodations_list = agents.retieve_hotel_names(location,names)
    lines = accomodations_list.splitlines()
    clean = []

    for line in lines:
        match = re.match(r"\d+\.\s*(.+)", line)
        if match:
            clean.append(match.group(1).strip())
    return clean