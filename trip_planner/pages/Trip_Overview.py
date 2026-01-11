import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import databaseManager
from API_Handlers import WeatherHandler
from API_Handlers import geoapify
from cognix_ai.cognix_ai import cognix_ai, get_top_attractions_for_ui
from config import settings

st.set_page_config(page_title="Trip Overview", page_icon="🧭", layout="wide")

# ----------------- Retrieve Trip -----------------
try:
    trip = st.session_state.get("current_trip", None)
except Exception as e:
    st.error(f"Error loading trip data: {e}")
    trip = None

if not trip:
    st.warning("No destination selected. Go to Explore to plan your trip.")
    st.stop()

place = trip.get("Place Name", "Unknown Destination")
attractive_points = geoapify.geoapify_attractions(place)
# ---- PLACE-SCOPED CHAT MEMORY ----
if "chat_histories" not in st.session_state:
    st.session_state["chat_histories"] = {}

if place not in st.session_state["chat_histories"]:
    st.session_state["chat_histories"][place] = []

chat_history = st.session_state["chat_histories"][place]

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
           
        else:
            lat, lon, _ = geoapify.geoapify_attractions(place)
            
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        lat, lon = 0, 0
        st.warning(f"Geocoding error for {place}: {e}. Defaulting to (0, 0).")

    # --- Things to Do Section ---
    with st.expander("🧳 Things to Do", expanded=True):
        st.write(f"Discover popular attractions around {place}.")

        result = databaseManager.get_things_to_do(place)

        if result["status"] == "error":
            _,_,raw_geo_data = geoapify.geoapify_attractions(place)
            
            attractions = get_top_attractions_for_ui(
                place=place,
                geoapify_data=raw_geo_data,
                llm=settings.llm
            )

            if not attractions:
                st.info("Fetching popular attractions using general knowledge.")
                attractions = cognix_ai(
                    user_input=f"List 10 popular tourist attractions in {place}",
                    username=st.session_state.get("user", "guest"),
                    place=place
                )

                if isinstance(attractions, str):
                    attractions = [
                        line.strip("- ").strip()
                        for line in attractions.split("\n")
                        if line.strip()
                    ][:10]

            databaseManager.set_things_to_do(place, attractions)

        else:
            attractions = result["data"]

        for idx, name in enumerate(attractions[:10], start=1):
            st.markdown(f"**{idx}. {name}**")

        # 🔑 store for chatbot reuse
        st.session_state["attractions"] = attractions


    # --- Weather Information Section ---
    with st.expander("🌦️ Weather Information", expanded=True):
        weather_details = WeatherHandler.weather_report(lat, lon, place)
        response = cognix_ai(
            user_input="Provide a detailed weather report based on the following data.",
            place=place,
            weather_data=weather_details,
            username=st.session_state.get("user", "guest")
        )
        st.session_state["weather_info"] = response
        with st.spinner('Fetching weather data...'):
            st.write(response)

# ----------------- RIGHT COLUMN -----------------
with right_col:
    st.subheader("💬 Trip Assistant Chatbot")
    st.markdown("Ask anything about your destination!")
    geo_data = geoapify.geoapify_attractions(place)
    st.session_state['geoapify_data'] = geo_data
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", placeholder="e.g. What’s the best time to visit?")
        send = st.form_submit_button("Send")

    if send and user_input:
        conversation_history = chat_history
        conversation_history.append({"role": "user", "content": user_input})

        response = cognix_ai(
            user_input=user_input,
            username=st.session_state.get("user", "guest"),
            conversation_history=conversation_history,
            place=place,
            weather_data = st.session_state.get("weather_info", ""),
            geoapify_data=geo_data
        )

        conversation_history.append({"role": "assistant", "content": response})

    for message in reversed(chat_history):
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
            result = databaseManager.save_a_trip(trip)

            if result["status"] == "exists":
                st.warning("This trip is already saved.")
                st.switch_page("pages/Home.py")
            elif result["status"] == "saved":
                st.success("Trip saved successfully!")
                st.switch_page("pages/Home.py")
            else:
                st.error(result["message"])

        except Exception as e:
            st.error(f"Error saving trip: {e}")

with col2:
    if st.button("🚀 Start Planning"):
        st.session_state["planning_started"] = True
        try:
            res = databaseManager.trip_plan(trip)
            if res:
                st.session_state["current_trip"]["Place Name"] = place
                st.switch_page("pages/Trip_Itinerary.py")
        except Exception as e:
            st.error(f"Error starting trip: {e}")

with col3:
    if st.button("⬅️ Back to Home"):
        st.switch_page("pages/Home.py")