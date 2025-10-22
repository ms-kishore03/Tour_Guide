import streamlit as st
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import explore
from Utilities import databaseManager

st.set_page_config(page_title="Explore", page_icon="🌍", layout="centered")

st.title("🌍 Explore The World")

# ---------- Trip Preferences ----------
scenario = st.selectbox(
    "Trip Theme",
    ["Adventure", "Relaxation", "Romantic", "Cultural", "Nature", "Luxury", "No Preference"]
)
activity = st.text_input("Specific activity (Required)", placeholder="e.g. hiking, museums, diving")
climate = st.selectbox("Preferred climate", ["Cool", "Warm", "Tropical", "Snowy", "No Preference"])
budget = st.selectbox("Budget per person", ["< $500", "$500–$1500", "$1500–$3000", "$3000+", "No Preference"])
duration = st.selectbox("Trip duration", ["Weekend", "3–5 days", "1 week", "2+ weeks", "No Preference"])
location = st.text_input("Preferred location (Required)", placeholder="e.g. Alps, Japan, Caribbean")
triptype = st.selectbox("Trip Type", ["Solo", "Couple", "Family", "Friends", "Group", "No Preference"])
transport = st.selectbox("Preferred transport", ["Car", "Bus", "Train", "Plane", "No Preference"])

col1, col2 = st.columns([3, 1])
with col1:
    find_button = st.button("Find me a place ➡️", use_container_width=True)
with col2:
    if st.button("🔄 Start Over", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ["user"]:
                del st.session_state[key]
        st.rerun()

# ---------- Logic ----------
if find_button:
    errors = []
    if not location:
        errors.append("Please fill in the required field: 'Preferred location'")
    if not activity:
        errors.append("Please fill in the required field: 'Specific activity'")
    if errors:
        for error in errors:
            st.error(error)
    else:
        with st.spinner("Finding the perfect destination for you..."):
            time.sleep(2)
            places, descriptions = explore.suggest_places(
                scenario, activity, climate, budget, duration, location, triptype, transport
            )
            st.session_state.places = places
            st.session_state.descriptions = descriptions
            st.success("Here are some recommendations for you:")

# ---------- Minimal Results ----------
if "places" in st.session_state and st.session_state.places:

    st.markdown("""
        <style>
        .place-box {
            padding: 1rem 1.2rem;
            border-radius: 12px;
            background-color: #1e1e1e;
            transition: background-color 0.2s ease;
            margin-bottom: 0.8rem;
        }
        .place-box:hover {
            background-color: #2a2a2a;
        }
        .place-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: white;
        }
        .place-desc {
            font-size: 0.9rem;
            color: #b0b0b0;
            margin-top: 0.2rem;
            margin-bottom: 0.4rem;
        }
        .select-btn {
            background: none;
            border: none;
            color: #00b4d8;
            font-size: 0.9rem;
            cursor: pointer;
            padding: 0;
        }
        .select-btn:hover {
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)

    for i, place in enumerate(st.session_state.places):
        desc = st.session_state.descriptions[i][:180] + "..."  # short description
        full_desc = st.session_state.descriptions[i]
        st.markdown(
            f"""
            <div class="place-box">
                <div class="place-title">{place}</div>
                <div class="place-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button(f"View →", key=f"select_{i}"):
            st.session_state.current_trip = {
                "Place Name": place,
                "Scenario": scenario,
                "Climate": climate,
                "Duration": duration,
                "People": triptype,
                "Transport": transport,
                "Description": full_desc
            }
            curr_trip = st.session_state.current_trip
            st.success(f"Selected {place}! Redirecting to Trip Overview...")
            time.sleep(1)
            st.switch_page("pages/Trip_Overview.py")
