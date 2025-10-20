from pymongo import MongoClient
import bcrypt
import streamlit as st

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

def save_a_trip(trip_details):
    username = st.session_state.user
    db = client['Tour_Guide']
    collection = db['Saved_Trips']
    trip_data = trip_details

    if not username:
        return "User not logged in."
    
    elif not trip_data:
        return "No trip data."

    trip_entry = {
        "username": username,
        "trip_data": trip_data
    }
    collection.insert_one(trip_entry)
    return "Trip saved successfully!"

def get_saved_trips():
    username = st.session_state.user
    db = client['Tour_Guide']
    collection = db['Saved_Trips']

    saved_trips = list(collection.find({"username": username}))

    # Extract trip_data (each is a dict)
    trips = [entry["trip_data"] for entry in saved_trips if "trip_data" in entry]
    return trips