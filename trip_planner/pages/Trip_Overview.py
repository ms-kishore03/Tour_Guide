import streamlit as st
from datetime import datetime
from streamlit_folium import st_folium
import folium
from utils import init_session_state

init_session_state()
st.set_page_config(page_title="Trip Overview", page_icon="🧭", layout="centered")

if not st.session_state.current_trip:
    st.warning("No destination selected. Go to Explore to plan your trip.")
    st.stop()

trip = st.session_state.current_trip
place = trip.get("Place Name", "Unknown Destination")

st.title(f"🧭 {place}")
st.markdown(f"""
**Scenario:** {trip.get('Scenario', 'N/A')}  
**Climate:** {trip.get('Climate', 'N/A')}  
**Duration:** {trip.get('Duration', 'N/A')}  
**People:** {trip.get('People', 'N/A')}  
**Transport:** {trip.get('Transport', 'N/A')}  
""")

st.divider()
tab1, tab2, tab3 = st.tabs(["🗺️ Map", "🌦️ Weather", "📰 News"])

# --- Map Tab ---
with tab1:
    coords = {
        "Paris": [48.8566, 2.3522],
        "Zermatt, Switzerland": [46.0207, 7.7491],
        "Queenstown, New Zealand": [-45.0312, 168.6626],
        "Banff, Canada": [51.1784, -115.5708]
    }
    lat, lon = coords.get(place, [48.8566, 2.3522])
    m = folium.Map(location=[lat, lon], zoom_start=11)
    folium.Marker([lat, lon], popup=place).add_to(m)
    st_folium(m, width=700, height=500)

# --- Weather Tab ---
with tab2:
    st.info("🌤️ Weather data will appear here (API integration placeholder).")

# --- News Tab ---
with tab3:
    st.info("🗞️ Latest news about this destination will appear here (API placeholder).")

st.divider()
if st.button("💾 Save Trip"):
    trip_to_save = trip.copy()
    trip_to_save["Saved Date"] = str(datetime.now().date())

    if trip_to_save not in st.session_state.saved_trips:
        st.session_state.saved_trips.append(trip_to_save)
        st.success("Trip saved! View it on Home 🏡")
    else:
        st.info("This trip is already saved.")


if st.button("⬅️ Back to Home"):
    st.switch_page("pages/Home.py")
