import streamlit as st
import pandas as pd
from datetime import datetime

# Check if logged in
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Please log in to access the Explore page.")
    st.switch_page("app.py")
    st.stop()

st.markdown('<h1 class="main-header">Explore Page</h1>', unsafe_allow_html=True)
st.markdown("<h2 class='sub-header'>Have a plan in mind?</h2>", unsafe_allow_html=True)

have_plan = st.radio("Have a plan in mind?", ("Yes", "No"))

if have_plan == "Yes":
    with st.form("trip_details"):
        place_name = st.text_input("Place Name")
        date = st.date_input("Date")
        num_people = st.number_input("No of People", min_value=1)
        transport_type = st.selectbox("Transport Type", ["Car", "Bus", "Train", "Plane", "Other"])
        climate = st.text_input("Climate (Auto-filled by AI)", value="Warm", disabled=True)  # Simulated auto-fill
        scenario = st.text_input("Scenario (Auto-filled by AI)", value="Adventure", disabled=True)
        location = st.text_input("Location (Auto-filled by AI)", value="Urban", disabled=True)
        trip_type = st.text_input("Trip Type (Auto-filled by AI)", value="Weekend", disabled=True)
        submitted = st.form_submit_button("Save Trip / Get Recommendations")
        if submitted:
            if place_name and date and num_people and transport_type:
                # Simulate AI recommendations
                recommendations = f"Personalized recommendations for {place_name}: Visit local attractions, enjoy cuisine. Use chatbot for more."
                st.session_state.current_trip = {
                    "Place Name": place_name,
                    "Date": date,
                    "No of People": num_people,
                    "Transport Type": transport_type,
                    "Climate": climate,
                    "Scenario": scenario,
                    "Location": location,
                    "Trip Type": trip_type,
                    "Recommendations": recommendations
                }
                st.success("Details processed! Check below.")
            else:
                st.error("Please fill required fields.")

elif have_plan == "No":
    query = st.text_input("What is it? (Describe your idea)")
    if st.button("Fill the details to get personalized Recommendations"):
        if query:
            # Simulate filling details and recommendations
            st.session_state.current_trip = {
                "Query": query,
                "Place Name": "Suggested: Paris",
                "Date": datetime.now().date(),
                "No of People": 2,
                "Transport Type": "Plane",
                "Climate": "Temperate",
                "Scenario": "Romantic",
                "Location": "Europe",
                "Trip Type": "Vacation",
                "Recommendations": f"Based on '{query}', recommend Paris: Eiffel Tower, etc."
            }
            st.success("Recommendations generated!")

# Display current trip if available
if 'current_trip' in st.session_state and st.session_state.current_trip:
    st.subheader("Info & Recommendations with Chatbot")
    st.json(st.session_state.current_trip)  # Display as JSON for simplicity

    st.subheader("Elaboration")
    st.write("Recommendation from LLM")
    st.write(st.session_state.current_trip.get("Recommendations", "No recommendations yet."))

    chatbot_input = st.text_input("Chatbot: Ask for more details")
    if st.button("Send to Chatbot"):
        if chatbot_input:
            st.write(f"**Bot Response:** Elaborating on {chatbot_input}: More info here (simulated).")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start this trip"):
            st.success("Trip started! Enjoy!")
    with col2:
        if st.button("Save this trip"):
            trip_to_save = st.session_state.current_trip.copy()
            trip_to_save["Saved Date"] = datetime.now().date()
            st.session_state.saved_trips.append(trip_to_save)
            st.success("Trip saved! Check in Home page.")
            del st.session_state.current_trip  # Clear after save