import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import databaseManager
from API_Handlers import WeatherHandler
import agents

st.set_page_config(page_title="Trip Overview", page_icon="🧭", layout="wide")

# ----------------- Retrieve Trip -----------------
try:
    trip = st.session_state.get("current_trip", None)
    print(f"Retrieved current_trip from st.session_state: {trip}")
except Exception as e:
    print(f"Error retrieving current_trip: {e}")
    st.error(f"Error loading trip data: {e}")
    trip = None

if not trip:
    st.warning("No destination selected. Go to Explore to plan your trip.")
    st.stop()

place = trip.get("Place Name", "Unknown Destination")

# ----------------- Page Header -----------------
st.title(f"🧭 Trip to {place}")

# ----------------- Trip Details (Full Width) -----------------
st.markdown("### Trip Details")
st.markdown(f"""
- **Destination**: {place}  
- **Scenario**: {trip.get('Scenario', 'N/A')}  
- **Climate**: {trip.get('Climate', 'N/A')}  
- **Duration**: {trip.get('Duration', 'N/A')}  
- **People**: {trip.get('People', 'N/A')}  
- **Transport**: {trip.get('Transport', 'N/A')}  
- **Description**: {trip.get('Description', 'No description available')}  
""")

st.divider()

# ----------------- Split Layout -----------------
left_col, right_col = st.columns([1, 1])  # Left: Weather + Things to Do | Right: Chatbot

# ----------------- LEFT COLUMN -----------------
with left_col:
    # --- Get Coordinates for Weather ---
    try:
        geolocator = Nominatim(user_agent="trip_planner_app")
        location = geolocator.geocode(place, timeout=10)
        if location:
            lat, lon = location.latitude, location.longitude
            #print(f"Geocoded {place} to coordinates: ({lat}, {lon})")
        else:
            lat, lon = 0, 0
            st.warning(f"Could not find coordinates for {place}. Defaulting to (0, 0).")
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        lat, lon = 0, 0
        st.warning(f"Geocoding error for {place}: {e}. Defaulting to (0, 0).")

    # --- Things to Do Section ---
    with st.expander("🧳 Things to Do", expanded=True):
        st.write("Discover fun activities, attractions, and local experiences around your destination.")
        st.write("Here are a few suggestions:")
        # Placeholder for integration with agents or API
        places = agents.get_attractive_points(place)
        for idx,p in enumerate(places, start=1):
            st.markdown(f"{idx}. {p}")

    # --- Weather Information Section ---
    with st.expander("🌦️ Weather Information", expanded=True):
        #print("Fetching weather data for:", place)
        weather_details = WeatherHandler.Weather_Explainer(lat, lon, place)
        st.session_state.weather_info = weather_details
        with st.spinner('Fetching weather data...'):
            st.write(weather_details)

# ----------------- RIGHT COLUMN -----------------
with right_col:
    st.subheader("💬 Trip Assistant Chatbot")
    st.markdown("Ask anything about your destination!")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", placeholder="e.g. What’s the best time to visit?")
        send = st.form_submit_button("Send")

    if send and user_input:
        conversation_history = st.session_state.get("chat_history")
        conversation_history.append({"role": "user", "content": user_input})
        response = agents.chatbot(
            conversation_history, user_input, st.session_state.get("weather_info", "")
        )
        conversation_history.append({"role": "assistant", "content": response})
        st.session_state["chat_history"] = conversation_history

    for message in reversed(st.session_state["chat_history"]):
        if message['role'] == 'user':
            st.chat_message("user").markdown(f"{message['content']}")
        else:
            st.chat_message("assistant").markdown(f"{message['content']}")

st.divider()

# ----------------- Bottom Action Buttons -----------------
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("💾 Save Trip"):
        try:
            databaseManager.save_a_trip(trip)
            st.success("Trip saved successfully!")
            st.switch_page("pages/Home.py")
        except Exception as e:
            st.error(f"Error saving trip: {e}")

with col2:
    if st.button("🚀 Start Planning"):
        st.session_state["planning_started"] = True
        try:
            res = databaseManager.start_trip(trip)
            if res:
                st.success("Let's start planning your adventure!")
                st.switch_page("pages/Trip_Itinerary.py")
        except Exception as e:
            st.error(f"Error starting trip: {e}")

with col3:
    if st.button("⬅️ Back to Home"):
        print("Navigating back to Home.py")
        st.switch_page("pages/Home.py")
