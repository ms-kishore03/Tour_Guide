import streamlit as st
from datetime import datetime, timedelta
from config import settings
from config.settings import mongo_db_client as client

client = settings.mongo_db_client
db = client['Tour_Guide']

def insert_place(Trip_Theme, Specific_Activity, Climate, budget, duration, Location, TripType, Transport, Places,Definitions):

  

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

    collection = db['Saved_Trips']

    saved_trips = list(collection.find({"username": username}))

    trips = [entry["trip_data"] for entry in saved_trips if "trip_data" in entry]
    return trips

def delete_saved_trip(trip):
    username = st.session_state.user

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

def save_ongoing_trips(username, place):

    # get trip details
    trip_details_collection=db["Saved_Trips"]
    docs = trip_details_collection.find_one(
        {"username": username, "trip_data.Place Name": place},
        {"_id": 0, "trip_data": 1}
    )
    trip_details = {
        
            "Place Name": docs["trip_data"]["Place Name"],
            "Scenario": docs["trip_data"]["Scenario"],
            "Duration": docs["trip_data"]["Duration"],
            "Climate": docs["trip_data"]["Climate"],
            "People": docs["trip_data"]["People"],
            "Transport": docs["trip_data"]["Transport"],
            "Description": docs["trip_data"]["Description"]
        
    }if docs else {}

    # Save ongoing trip
    
    save_trip_data = {
        "username": username,
        "place": place,
        "trip_details": trip_details if trip_details else []
    }

    ongoing_trips_collection = db["Ongoing_Trips"]
    try:
        ongoing_trips_collection.update_one(
            {"username": username, "place": place},
            {"$set": save_trip_data},
            upsert=True
        )
        return {"status": "ok"}
    except Exception:
        return {"status": "error", "message": "Failed to save ongoing trip."}


def get_ongoing_trip(username):

    collection = db["Ongoing_Trips"]

    doc = collection.find_one(
        {"username": username},
        {"_id": 0}
    )
    return doc

def save_expenses(username, place, expenses):
    collection = db["Ongoing_Trips"]

    try:
        result = collection.update_one(
            {"username": username, "place": place},
            {
                "$set": {
                    "username": username,
                    "place": place,
                    "expenses": expenses
                }
            },
            upsert=True
        )

        return {"status": "ok"}

    except Exception as e:
        print("ERROR:", e)
        return {"status": "error", "message": str(e)}

    
def get_expenses(username, place):
    collection = db["Ongoing_Trips"]

    doc = collection.find_one(
        {"username": username, "place": place},
        {"_id": 0, "expenses": 1}
    )

    return doc.get("expenses", []) if doc else []

def end_ongoing_trip(username ,place):
    collection = db["Ongoing_Trips"]
    collection.delete_one({"username": username, "place": place})
