import streamlit as st
import time
from utils import init_session_state

# -------------------- INIT --------------------
init_session_state()
st.set_page_config(page_title="Explore", page_icon="🌍", layout="centered")

# Redirect to login if user not logged in
if not st.session_state.user:
    st.switch_page("Login_Register.py")

st.title("🌍 Explore Trips")

have_plan = st.radio("Do you already have a plan?", ("No", "Yes"), horizontal=True)

# =========================================================
# USER HAS NO PLAN
# =========================================================
if have_plan == "No":
    step = st.session_state.explore_step

    # -------------------- STEP 1 --------------------
    if step == 1:
        st.subheader("Step 1: Choose Experience")
        scenario = st.selectbox(
            "Trip Theme",
            ["Adventure", "Relaxation", "Romantic", "Cultural", "Nature", "Luxury"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Home"):
                st.switch_page("pages/Home.py")

        with col2:
            if st.button("Next ➡️"):
                st.session_state["scenario"] = scenario
                st.session_state.explore_step = 2
                st.rerun()

    # -------------------- STEP 2 --------------------
    elif step == 2:
        st.subheader("Step 2: Preferences")
        activity = st.text_input(
            "Any specific activity?", placeholder="e.g. hiking, museums, diving"
        )
        climate = st.selectbox(
            "Preferred climate",
            ["Cool", "Warm", "Tropical", "Snowy", "No Preference"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.explore_step = 1
                st.rerun()
        with col2:
            if st.button("Next ➡️"):
                st.session_state["activity"] = activity
                st.session_state["climate"] = climate
                st.session_state.explore_step = 3
                st.rerun()

    # -------------------- STEP 3 --------------------
    elif step == 3:
        st.subheader("Step 3: Trip Details")

        num_people = st.number_input("How many people are going?", min_value=1, value=2)
        budget = st.selectbox(
            "Budget per person", ["< $500", "$500–$1500", "$1500–$3000", "$3000+"]
        )
        duration = st.selectbox(
            "Trip duration", ["Weekend", "3–5 days", "1 week", "2+ weeks"]
        )
        transport = st.selectbox(
            "Preferred transport", ["Car", "Bus", "Train", "Plane", "No Preference"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.explore_step = 2
                st.rerun()
        with col2:
            if st.button("🧭 Generate Destinations"):
                with st.spinner("Finding destinations..."):
                    time.sleep(2)

                # Store trip preferences
                st.session_state.trip_preferences = {
                    "Scenario": st.session_state.scenario,
                    "Activity": st.session_state.activity,
                    "Climate": st.session_state.climate,
                    "People": num_people,
                    "Budget": budget,
                    "Duration": duration,
                    "Transport": transport,
                }

                # Dummy suggestions (replace with real API or model later)
                st.session_state.destination_suggestions = [
                    {"Place": "Zermatt, Switzerland", "Why": "Perfect for skiing and adventure."},
                    {"Place": "Queenstown, New Zealand", "Why": "Adventure capital with scenic beauty."},
                    {"Place": "Banff, Canada", "Why": "Nature, snow, and group activities."},
                ]

                st.session_state.explore_step = 4
                st.rerun()

    # -------------------- STEP 4 --------------------
    elif step == 4:
        st.subheader("🏔️ Suggested Destinations")

        for idx, dest in enumerate(st.session_state.destination_suggestions, start=1):
            st.markdown(f"**{idx}. {dest['Place']}** — {dest['Why']}")

            if st.button(f"Select {dest['Place']}", key=f"sel_{idx}"):
                # Set current trip (but DO NOT auto-save)
                st.session_state.current_trip = {
                    "Place Name": dest["Place"],
                    **st.session_state.trip_preferences
                }

                # Navigate to trip overview for review
                st.switch_page("pages/Trip_Overview.py")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back"):
                st.session_state.explore_step = 3
                st.rerun()
        with col2:
            if st.button("🔄 Start Over"):
                st.session_state.e_
