import requests
import os
from dotenv import load_dotenv

load_dotenv(".env")
API_Key = os.getenv("Flight_API_Key")

url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"

querystring = {
    "departure_id": "LAX",
    "arrival_id": "JFK",
    "outbound_date": "2025-12-25",
    "return_date": "2026-01-05",
    "travel_class": "ECONOMY",  # Options: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
    "adults": "1",
    "children": "0",
    "currency": "USD",
    "language_code": "en-US",
    "country_code": "US",
    "search_type": "cheap" # Options: cheap, best
}

headers = {
    "x-rapidapi-key": API_Key,
    "x-rapidapi-host": "google-flights2.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring).json()

def get_flight_info(response):
    # ✅ Check response safely
    if not response or "data" not in response:
        print("No flight data available.")
        return
    
    itineraries = response["data"].get("itineraries", {})
    if "topFlights" not in itineraries:
        print("No topFlights key found in response.")
        return

    for flight in itineraries["topFlights"]:
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

        flight_info = f"""
Flight from {departure_airport_name} ({departure_airport_code}) → {arrival_airport_name} ({arrival_airport_code})
Departure: {dept_time} | Arrival: {arr_time}
Duration: {duration}, Airline: {airline}, Flight No: {flight_number}
Layovers: {layover_count}, Carry-on: {carry_on}, Checked: {checked_bags}
Price: ${price}, Carbon Difference: {carbon_diff}%
--------------------------------------------------------
"""
        print(flight_info)


get_flight_info(response)