import requests
import os
from dotenv import load_dotenv
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import databaseManager

# ✅ Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
API_Key = os.getenv("Flight_API_Key")

#def get_airport_id(city_name):
#    print("Fetching airport code for city:", city_name)
#    code = databaseManager.airport_codes(city_name)
#    print(code)
#    return code
#
    #url = "https://google-flights2.p.rapidapi.com/api/v1/searchAirport"
#
#    #querystring = {"query": city_name, "language_code": "en-US", "country_code": "US"}
#
#    #headers = {
#    #    "x-rapidapi-key": API_Key,
#    #    "x-rapidapi-host": "google-flights2.p.rapidapi.com"
#    #}
#
#    #try:
#    #    airport_id_response = requests.get(url, headers=headers, params=querystring).json()
#    #    data = airport_id_response.get("data", [])
#    #    if not data or not isinstance(data, list):
#    #        print(f"❌ No airport data found for city: {city_name}")
#    #        return None
#
#    #    airport_list = data[0].get("list", [])
#    #    if not airport_list:
#    #        print(f"❌ No airport found in list for city: {city_name}")
#    #        return None
#
#    #    airport_id = airport_list[0].get("id")
#    #    airport_name = airport_list[0].get("title")
#    #    print(f"✅ Found airport for {city_name}: {airport_name} ({airport_id})")
#    #    return airport_id
#
#    #except Exception as e:
    #    print(f"⚠️ Error processing airport data for {city_name}: {e}")
    #    return None


def get_flight_info(departure_airport, arrival_airport, departure_date, return_date,
                    travel_class, adults, children, currency, search_type):

    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"

    querystring = {
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": departure_date,
        "return_date": return_date,
        "travel_class": travel_class,  # ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
        "adults": adults,
        "children": children,
        "currency": currency,
        "language_code": "en-US",
        "country_code": "US",
        "search_type": search_type  # cheap, best
    }

    headers = {
        "x-rapidapi-key": API_Key,
        "x-rapidapi-host": "google-flights2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring).json()
    except Exception as e:
        return [f"API request failed: {e}"]

    
    if not response:
        return ["No response from API."]

    if "data" not in response:
        return [f"Unexpected API format: {response}"]

    itineraries = response["data"].get("itineraries", {})
    if not itineraries or "topFlights" not in itineraries:
        return ["No top flights data found."]

    top_flights = itineraries.get("topFlights", [])
    if not top_flights:
        return ["No available flights found."]

    flight_options = []
    for flight in top_flights:
        dept_time = flight.get("departure_time", "N/A")
        arr_time = flight.get("arrival_time", "N/A")
        duration = flight.get("duration", {}).get("text", "N/A")

        flight_details = flight["flights"][0] if flight.get("flights") else {}
        departure_airport_name = flight_details.get("departure_airport", {}).get("airport_name", "N/A")
        departure_airport_code = flight_details.get("departure_airport", {}).get("airport_code", "N/A")
        arrival_airport_name = flight_details.get("arrival_airport", {}).get("airport_name", "N/A")
        arrival_airport_code = flight_details.get("arrival_airport", {}).get("airport_code", "N/A")
        airline = flight_details.get("airline", "N/A")
        flight_number = flight_details.get("flight_number", "N/A")

        layovers = flight.get("layovers") or []
        layover_count = len(layovers)

        bags = flight.get("bags", {})
        carry_on = bags.get("carry_on", "N/A")
        checked_bags = bags.get("checked", "N/A")

        price = flight.get("price", "N/A")

        carbon = flight.get("carbon_emissions", {})
        carbon_diff = carbon.get("difference_percent", "N/A")

        flight_options.append({
        "Airline": airline,
        "Flight #": flight_number,
        "From": f"{departure_airport_name} ({departure_airport_code})",
        "To": f"{arrival_airport_name} ({arrival_airport_code})",
        "Departure": dept_time,
        "Arrival": arr_time,
        "Duration": duration,
        "Layovers": len(layovers),
        "Carry-on": bags.get("carry_on", "N/A"),
        "Checked Bags": bags.get("checked", "N/A"),
        "Price": f"{currency} {flight.get('price', 'N/A')}",
        "Carbon Δ (%)": carbon.get("difference_percent", "N/A")
    })

    return pd.DataFrame(flight_options)