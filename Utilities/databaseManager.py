import streamlit as st
from datetime import datetime, timedelta
from config import settings

client = settings.mongo_db_client

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

#---------------------------------------#
# This function is used to add a task to an existing document with matching username and place
#---------------------------------------#
def add_task_existing_place(username, place, task):

    db = client['Tour_Guide']
    collection = db['User_Plans']

    result = collection.update_one(
        {"username": username, "plans.place": place},
        {"$push": {"plans.$.tasks": {"task": task}}}
    )
    return result.matched_count > 0

#---------------------------------------#
# This function is used to add a task to a new document with corresponding username and place
#---------------------------------------#
def add_task_new_place(username, place, task):

    db = client['Tour_Guide']
    collection = db['User_Plans']
    collection.update_one(
        {"username": username},
        {
            "$push": {
                "plans": {
                    "place": place,
                    "tasks": [{"task": task}] # datatype --> array of objects
                }
            }
        },
        upsert=True # if the document doesn't exist, it will be created
    )

def ensure_user(username):
    db = client['Tour_Guide']
    col = db['User_Plans']
    col.update_one(
        {"username": username},
        {"$setOnInsert": {"plans": []}},
        upsert=True
    )

def add_todo(username, place, task):
    ensure_user(username)
    exists = add_task_existing_place(username, place, task) # if the document exists, it will be updated
    if not exists:
        add_task_new_place(username, place, task) # if the document doesn't exist, it will be created


def get_todo(username, place):
    db = client['Tour_Guide']
    collection = db['User_Plans']
    user = collection.find_one({"username": username}, {"_id": 0})  # get the user document
    if not user:
        return []

    for plan in user.get("plans", []): # get the correct plan from the user document
        if plan.get("place") == place:
            return [t.get("task") for t in plan.get("tasks", [])]

    return []

def get_itinerary_from_db(collection, username, place):
    doc = collection.find_one(
        {"username": username, "place": place},
        {"_id": 0, "itinerary_list": 1}
    )
    if not doc:
        return []
    return doc.get("itinerary_list", [])
