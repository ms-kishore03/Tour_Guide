from google import genai
import os
from dotenv import load_dotenv
import Utilities.databaseManager as databaseManager

# ---------- ENV SETUP ----------
os.environ.pop("GROQ_API_KEY", None)
load_dotenv()

# ---------- FUNCTION 1: Suggest Places ----------
def suggest_places(Trip_Theme, Specific_Activity, Climate, budget, duration, Location, TripType, Transport):
    # Check if entry exists in MongoDB
    existing_entry = databaseManager.collection.find_one({
        "Trip_Theme": Trip_Theme,
        "Specific_Activity": Specific_Activity,
        "Climate": Climate,
        "Budget": budget,
        "Duration": duration,
        "Location": Location,
        "TripType": TripType,
        "Transport": Transport
    })
    
    if existing_entry:
        print("Fetching from database...")
        return existing_entry["Places"], existing_entry.get("Descriptions", [])

    # Else, call Gemini API
    print("Fetching from Gemini API...")
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # ---------- Fetch from Gemini for Places ----------
    validation = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
        You are a trip organizer agent.
        You are given the following:
        - Trip_Theme: {Trip_Theme}
        - Specific_Activity: {Specific_Activity}
        - Climate: {Climate}
        - Budget: {budget}
        - Duration: {duration}
        - Location: {Location}
        - TripType: {TripType}
        - Transport: {Transport}

        Task: Suggest 5 best tourist places to visit based on the inputs.
        Output format: Only list the place names, one per line. 
        No numbering, no bullet points, no extra text.
        """
    )

    try:
        text_output = validation.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print("Error reading Gemini response:", e)
        text_output = ""

    suggested_places = [p.strip("- ").strip() for p in text_output.split("\n") if p.strip()]

    # ---------- Get Place Descriptions ----------
    place_def = place_definition(suggested_places)

    # ---------- Store in MongoDB ----------
    databaseManager.insert_place(
        Trip_Theme, Specific_Activity, Climate,
        budget, duration, Location, TripType, Transport,
        suggested_places, place_def
    )

    return suggested_places, place_def


# ---------- FUNCTION 2: Place Definition ----------
def place_definition(places):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
        You are a travel guide agent.
        For each of the following places: {', '.join(places)},
        provide a short 2–3 line description including its location and one unique attraction.
        Output format:
        PlaceName: Description
        One per line. No bullets or numbering.
        """
    )

    try:
        text = response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print("Error reading Gemini response:", e)
        text = ""

    place_descriptions = {}
    for line in text.split("\n"):
        if ":" in line:
            name, desc = line.split(":", 1)
            place_descriptions[name.strip()] = desc.strip()

    return [place_descriptions.get(p, "") for p in places]
