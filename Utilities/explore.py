from langchain_groq import ChatGroq
import os
from google import genai
from dotenv import load_dotenv
import databaseManager

load_dotenv()

# function that suggests places to users if they have no plan in mind

def suggest_places(Climate, Scenario, Location, TripType, Transport):

    #check the mongo db for existing places
    #if exists return the places

    existing_entry = databaseManager.collection.find_one({
            "Climate": Climate,
            "Scenario": Scenario,
            "Location": Location,
            "TripType": TripType,
            "Transport": Transport
    })
    if existing_entry:
        print("Fetching from database...")
        return existing_entry["Places"]
    
    #else call gemini api to get the places

    else:
        print("Fetching from Gemini API...")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        suggested_places=[]
        validation = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(f"""
            You are a trip organizer agent. 
            You are given the following:
            - Climate: {Climate}
            - Scenario: {Scenario}
            - Location: {Location}
            - Trip Type: {TripType}
            - Transport: {Transport}

            Task: Suggest 5 best tourist places to visit based on the inputs.
            Output format: Only list the place names, one per line.
            """)
        )
        text = validation.text.strip().split("\n")
        for place in text:
            if place:
                suggested_places.append(place.strip("- ").strip())
        
        #store the places in mongo db
        databaseManager.insert_place(Climate, Scenario, Location, TripType, Transport, suggested_places)
        return suggested_places
    
# function that provides a brief description of the place

def place_definition(place):
    client = ChatGroq(api_key=os.getenv("GEMINI_API_KEY"))
    response=client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(f"""
        You are a travel guide agent.
        You are given the following place name: {place}
        Task: Provide a brief description of the place in 5-6 sentences.
        Provide detailed information about the place including its significance, location, and any interesting facts and points of interest.
        Output format: Provide the description in points format.
        """)
    )
    return response.text.strip()
