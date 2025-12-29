from pymongo import MongoClient
import bcrypt
import streamlit as st
from datetime import datetime, timezone, timedelta

client = MongoClient('mongodb+srv://tester_username:tester_password@ai-tour-guide.mzeft5j.mongodb.net/')

def insert_place(Trip_Theme, Specific_Activity, Climate, budget, duration, Location, TripType, Transport, Places,Definitions):

    # Access the database
    db = client['Tour_Guide']

    collection = db['Places_Database']

    place_entry = {
        "Trip_Theme": Trip_Theme,
            "Specific_Activity": Specific_Activity,
            "Climate": Climate,
            "Budget": budget,
            "Duration": duration,
            "Location": Location,
            "TripType": TripType,
            "Transport": Transport,
            "Places": Places,
            "Descriptions": Definitions
    }
    collection.insert_one(place_entry)
    return "Place data inserted successfully!"

def set_things_to_do(destination, interests):
    if not destination or not interests:
        return {"status": "error", "message": "Destination or interests missing"}
    
    db = client['Tour_Guide']
    collection = db["Things_To_Do"]

    match = collection.find_one({
        "destination": destination,
        "interests": interests
    })

    if match:
        return {"status": "exists"}
    
    now = datetime.now()
    collection.insert_one({
        "destination": destination,
        "interests": interests,
        "timestamp": now
    })
    return {"status": "saved"}

def get_things_to_do(destination):
    if not destination:
        return {"status": "error", "data": None}

    db = client['Tour_Guide']
    collection = db["Things_To_Do"]

    entry = collection.find_one({"destination": destination})
    if not entry:
        return {"status": "error", "data": None}

    updated_at = entry.get("timestamp")
    if not updated_at or datetime.now() - updated_at > timedelta(weeks=2):
        collection.delete_one({"_id": entry["_id"]})
        return {"status": "error", "data": None}

    return {"status": "ok", "data": entry.get("interests", [])}

def save_a_trip(trip_details):
    username = st.session_state.get("user")

    if not username:
        return {"status": "error", "message": "User not logged in"}

    if not trip_details:
        return {"status": "error", "message": "No trip data"}

    db = client["Tour_Guide"]
    collection = db["Saved_Trips"]

    match = collection.find_one({
        "username": username,
        "trip_data": trip_details
    })

    if match:
        return {"status": "exists"}

    collection.insert_one({
        "username": username,
        "trip_data": trip_details
    })

    return {"status": "saved"}


def get_saved_trips():
    username = st.session_state.user
    db = client['Tour_Guide']
    collection = db['Saved_Trips']

    saved_trips = list(collection.find({"username": username}))

    # Extract trip_data (each is a dict)
    trips = [entry["trip_data"] for entry in saved_trips if "trip_data" in entry]
    return trips

def delete_saved_trip(trip):
    username = st.session_state.user
    db = client['Tour_Guide']
    collection = db['Saved_Trips']

    if not username:
        return "User not logged in."

    elif not trip:
        return "No trip data."

    result = collection.delete_one({"username": username, "trip_data": trip})

    if result.deleted_count > 0:
        return True
    else:
        return False


def trip_plan(trip_details):
    
    username = st.session_state.user
    if not username:
        return "User not logged in."
    
    elif not trip_details:
        return "No trip data."

    db = client['Tour_Guide']
    collection = db['Planning_Trips']    
    
    match = collection.find_one({
        "username": username,
        "trip_data": trip_details
    })
    if match:
        return True
    
    trip_entry = {
        "username": username,
        "trip_data": trip_details
    }

    collection.insert_one(trip_entry)
    return True
    

def airport_codes(name):
    db = client["Tour_Guide"]
    collection = db["Airports"]
    airport = collection.find_one({"name": {"$regex": name, "$options": "i"}})
    if airport:
        return airport.get("code")
    return None