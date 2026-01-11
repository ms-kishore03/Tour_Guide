from serpapi import GoogleSearch
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()
API_Key = os.getenv("SERPAPI_API_KEY")

def get_flight_details(departure_id, arrival_id, outbound_date, return_date,currency,travel_class,trip_type,adults,children,infants_in_seat,infants_in_lap):

  params = {
    "engine": "google_flights",
    "hl": "en",
    "gl": "us",
    "departure_id": departure_id,
    "arrival_id": arrival_id,
    "outbound_date": outbound_date,
    "return_date": return_date,
    "currency": currency,
    "travel_class": travel_class, #1 - Economy (default) 2 - Premium economy 3 - Business 4 - First
    "type": trip_type, #Round trip (default) 2 - One way 3 - Multi-city 
    "adults": adults,
    "children": children,
    "infants_in_seat": infants_in_seat,
    "infants_in_lap": infants_in_lap,
    "api_key": API_Key

  }

  search = GoogleSearch(params)
  results = search.get_dict()

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
      total_duration = f"{total_minutes//60} hrs {total_minutes%60} mins"

      layovers = len(flight.get("layovers", []))
      carbon_grams = flight.get("carbon_emissions", {}).get("this_flight", 0)
      carbon_emission = f"{carbon_grams/1000:.1f} kg CO2e"

      flight_options.append({
          "departure_time": dep,
            "arrival_time": arr,
            "airlines": airlines,
            "duration": total_duration,
            "layovers": layovers,
            "price": f"{price} {currency}" if price else "N/A",
            "carbon_emission": carbon_emission
     })
  return pd.DataFrame(flight_options)  
