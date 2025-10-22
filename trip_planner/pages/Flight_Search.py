import streamlit as st
from datetime import date, timedelta

# --- Page Config ---
st.set_page_config(page_title="✈️ Flight Finder", page_icon="✈️", layout="centered")

# --- Default querystring ---
querystring = {
    "departure_id": "LAX",
    "arrival_id": "JFK",
    "outbound_date": "2025-12-25",
    "return_date": "2026-01-05",
    "travel_class": "ECONOMY",
    "adults": "1",
    "children": "0",
    "currency": "USD",
    "language_code": "en-US",
    "country_code": "US",
    "search_type": "cheap"
}

# --- Title ---
st.title("✈️ Plan Your Flight Trip")

st.markdown("Find the best and cheapest flights for your next adventure!")

# --- Flight Search Form ---
with st.form("flight_search"):
    st.subheader("Flight Details")

    col1, col2 = st.columns(2)
    with col1:
        departure_id = st.text_input("Departure Airport (IATA Code)", querystring["departure_id"])
        outbound_date = st.date_input("Departure Date", date.fromisoformat(querystring["outbound_date"]))
        adults = st.number_input("Adults", min_value=1, max_value=9, value=int(querystring["adults"]))
        travel_class = st.selectbox(
            "Travel Class",
            ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"],
            index=["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"].index(querystring["travel_class"])
        )
    with col2:
        arrival_id = st.text_input("Arrival Airport (IATA Code)", querystring["arrival_id"])
        return_date = st.date_input("Return Date", date.fromisoformat(querystring["return_date"]))
        children = st.number_input("Children", min_value=0, max_value=9, value=int(querystring["children"]))
        search_type = st.radio("Search Type", ["cheap", "best"], index=["cheap", "best"].index(querystring["search_type"]))

    currency = st.selectbox("Currency", ["USD", "EUR", "INR", "GBP"], index=0)

    # --- Submit Button ---
    submitted = st.form_submit_button("🔍 Search Flights")

# --- Display Results ---
if submitted:
    st.success("Searching for flights... ✈️")

    # Simulate querystring generation
    query = {
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date.strftime("%Y-%m-%d"),
        "return_date": return_date.strftime("%Y-%m-%d"),
        "travel_class": travel_class,
        "adults": adults,
        "children": children,
        "currency": currency,
        "language_code": querystring["language_code"],
        "country_code": querystring["country_code"],
        "search_type": search_type
    }

    st.write("### Generated Query Parameters")
    st.json(query)

    # Mock result display
    st.info("💡 (Demo) Connect to a flight API like Amadeus, Skyscanner, or Kiwi to show real results.")
    st.write("**Example results:**")
    st.table([
        {"Airline": "Delta", "Price": "$420", "Duration": "5h 30m", "Stops": "Non-stop"},
        {"Airline": "American Airlines", "Price": "$450", "Duration": "5h 45m", "Stops": "Non-stop"},
        {"Airline": "United", "Price": "$390", "Duration": "6h 10m", "Stops": "1 stop"},
    ])
