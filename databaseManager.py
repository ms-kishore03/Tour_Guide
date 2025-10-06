from pymongo import MongoClient
import bcrypt

client = MongoClient('mongodb+srv://tester_username:tester_password@ai-tour-guide.mzeft5j.mongodb.net/')

# Access the database
db = client['Tour_Guide']

collection = db['Places_Database']

def insert_place(Climate, Scenario, Location, TripType, Transport,place_data):
    place_entry = {
        "Climate": Climate,
        "Scenario": Scenario,
        "Location": Location,
        "TripType": TripType,
        "Transport": Transport,
        "Places": place_data
    }
    collection.insert_one(place_entry)
    return "Place data inserted successfully!"


