from pymongo import MongoClient
import bcrypt

client = MongoClient('mongodb+srv://tester_username:tester_password@ai-tour-guide.mzeft5j.mongodb.net/')

# Access the database
db = client['Tour_Guide']

collection = db['Places_Database']

def insert_place(Trip_Theme, Specific_Activity, Climate, budget, duration, Location, TripType, Transport, Places,Definitions):
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


