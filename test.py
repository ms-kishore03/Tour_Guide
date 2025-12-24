# booking_autocomplete.py
# Run this in VS Code with: python booking_autocomplete.py

import requests
import json

def get_location_autocomplete(query):
    url = "https://booking-com18.p.rapidapi.com/stays/auto-complete"

    querystring = {
        "query": query
    }

    headers = {
        "x-rapidapi-key": "72ce0bd498msh5560318f80c4955p1c1164jsn455a66af5326",
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
        "x-rapidapi-key": "72ce0bd498msh5560318f80c4955p1c1164jsn455a66af5326",
        "x-rapidapi-host": "booking-com18.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    city = "Munnar"
    loc_res = get_location_autocomplete(city)

    # Pretty print JSON output
    #print(json.dumps(loc_res, indent=4))
    loc_id = loc_res["data"][0]["id"]
    print(f"Location ID for {city}: {loc_id}")
    checkin_date = "2026-01-02"
    checkout_date = "2026-01-08"

    stay_res = search_stays(loc_id, checkin_date, checkout_date)
    # Pretty-print full response
    #print(json.dumps(stay_res, indent=4))
    names=[]
    for i in range(10,0,-1):
        hotel_name = stay_res["data"][i]["name"]
        names.append(hotel_name)
    print("Top 5 hotel names:")
    for name in names:
        print(name)


