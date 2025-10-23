import streamlit as st
from datetime import date, timedelta
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from API_Handlers import FlightHandler

# --- Page Config ---
st.set_page_config(page_title="✈️ Flight Finder", page_icon="✈️", layout="centered")

# --- Default querystring ---


# --- Title ---
st.title("✈️ Plan Your Flight Trip")

st.markdown("Find the best and cheapest flights for your next adventure!")

# --- Flight Search Form ---
with st.form("flight_search"):
    st.subheader("Flight Details")

    col1, col2 = st.columns(2)
    with col1:
        departure = st.text_input("Departure Airport")
        outbound_date = st.date_input("Departure Date")
        adults = st.number_input("Adults", min_value=1)
        travel_class = st.selectbox(
            "Travel Class",
            ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
        )
    with col2:
        arrival = st.text_input("Arrival Airport")
        return_date = st.date_input("Return Date")
        children = st.number_input("Children",min_value=0)
        search_type = st.radio("Search Type", ["cheap", "best"])

    currency = st.selectbox("Currency", ["USD", "EUR", "INR", "GBP"], index=0)

    # --- Submit Button ---
    submitted = st.form_submit_button("🔍 Search Flights")

# --- Display Results ---
if submitted:
    st.success("Searching for flights... ✈️")

    #get airport codes
    departure_id = FlightHandler.get_airport_id(departure)
    arrival_id = FlightHandler.get_airport_id(arrival)

    st.write("### Generated Query Parameters")
    flight_options = FlightHandler.get_flight_info(departure_id,arrival_id,
                                                   outbound_date.strftime("%Y-%m-%d"),
                                                   return_date.strftime("%Y-%m-%d"),
                                                    travel_class, adults, children, currency, search_type)
    st.write("### Flight Options")
    st.write(flight_options)

