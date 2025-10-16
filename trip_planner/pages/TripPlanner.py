import streamlit as st
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import explore

st.set_page_config(page_title="Explore", page_icon="🌍", layout="centered")

st.title("🌍 Explore The World")

tab1, tab2 = st.tabs(["I do not have a plan", "I have a plan"])

# ---------- I DO NOT HAVE A PLAN ----------

with tab1:
    scenario = st.selectbox(
        "Trip Theme",
        ["Adventure", "Relaxation", "Romantic", "Cultural", "Nature", "Luxury"]
    )
    activity = st.text_input(
            "Do you want to perform any specific activity?", placeholder="e.g. hiking, museums, diving"
    )
    climate = st.selectbox(
            "Preferred climate",
            ["Cool", "Warm", "Tropical", "Snowy", "No Preference"]
    )
    
    budget = st.selectbox(
            "Budget per person", ["< $500", "$500–$1500", "$1500–$3000", "$3000+"]
    )
    duration = st.selectbox(
            "Trip duration", ["Weekend", "3–5 days", "1 week", "2+ weeks"]
    )
    location = st.text_input(
            "Any preferred location or region?", placeholder="e.g. Alps, Japan, Caribbean"
    )
    triptype=st.selectbox(
            "Trip Type", ["Solo", "Couple", "Family", "Friends", "Group", "No Preference"]
    )            
    transport = st.selectbox(
            "Preferred transport", ["Car", "Bus", "Train", "Plane", "No Preference"]
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back"):
            st.write("You are already at the first step.")
    with col2:
        if st.button("Find me a place ➡️"):
            if not scenario or not budget or not duration:
                st.error("Please fill in all required fields.")
            else:
                with st.spinner("Finding the perfect destination for you..."):
                    time.sleep(2)  # Simulate a delay for better UX
                    result = explore.suggest_places(
                        scenario, activity, climate, budget, duration, location, triptype, transport
                    )[0]
                    st.success("Here are some recommendations for you:")
                    st.markdown(result)

# ---------- I HAVE A PLAN ----------
with tab2:
    desired_place = st.text_input("Enter your desired destination", placeholder="e.g. Paris, Bali, New York")
    result = explore.place_definition(desired_place)
    if st.button("Get Definition"):
        if not desired_place:
            st.error("Please enter a destination.")
        else:
            with st.spinner("Fetching the definition..."):
                time.sleep(1)  # Simulate a delay for better UX
                st.success(f"Definition of {desired_place}:")
                st.markdown(result)       