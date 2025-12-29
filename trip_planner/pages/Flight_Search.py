import streamlit as st
from datetime import date, timedelta
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import agents
from API_Handlers import FlightHandler
from API_Handlers import FlightHandler_V2

# --- Page Config ---
st.set_page_config(page_title="Flight Finder", page_icon="✈️", layout="centered")

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
        children = st.number_input("Children",min_value=0)
        travel_class_label = st.selectbox(
            "Travel Class",
            ["Economy", "Premium Economy", "Business", "First Class"]
        )
        travel_class_mapping = {
            "Economy": "1",
            "Premium Economy": "2",
            "Business": "3",
            "First": "4"
        }
        travel_class = travel_class_mapping[travel_class_label]
    with col2:
        arrival = st.text_input("Arrival Airport")
        return_date = st.date_input("Return Date")
        infants_in_seat = st.number_input("Infants in Seat",min_value=0)
        infants_in_lap = st.number_input("Infants in Lap",min_value=0)
        search_type_label = st.selectbox("Trip Type", ["Round Trip", "One Way","Multi City"], index=0)
        currency = st.selectbox("Currency", [
            "ZAR","XPF","VND","USD","UAH","TWD","TRY","THB","SGD","SEK","SAR","RUB","RSD","RON","QAR",
            "PLN","PKR","PHP","PEN","PAB","OMR","NZD","NOK","MYR","MXN","MKD","MDL","MAD","LBP","KZT",
            "KWD","KRW","JPY","JOD","JMD","ISK","IRR","INR","ILS","IDR","HUF","HKD","GEL","GBP","EUR",
            "EGP","DZD","DOP","DKK","CZK","CUP","CRC","COP","CNY","CLP","CHF","CAD","BYN","BSD","BRL",
            "BMD","BHD","BGN","BAM","AZN","AWG","AUD","ARS","AMD","ALL","AED"  
        ], index=0)
    search_type_mapping = {
        "Round Trip": "1",
        "One Way": "2",
        "Multi City": "3"
    }
    trip_type = search_type_mapping[search_type_label]
    

    # --- Submit Button ---
    submitted = st.form_submit_button("🔍 Search Flights")


if "searching" not in st.session_state:
    st.session_state.searching = False

# --- Display Results ---

if submitted:
    st.session_state.searching = True

    if st.session_state.searching:
        status_placeholder = st.empty()
        status_placeholder.success("Searching for flights... ✈️")

        departure_id = agents.get_airport_id(departure)
        arrival_id = agents.get_airport_id(arrival)

        flight_options = FlightHandler_V2.get_flight_details(
            departure_id,
            arrival_id,
            outbound_date.strftime("%Y-%m-%d"),
            return_date.strftime("%Y-%m-%d") if trip_type == "1" else None,
            currency,
            travel_class,
            trip_type,
            adults,
            children,
            infants_in_seat,
            infants_in_lap
        )

        st.session_state.searching = False
        status_placeholder.empty()


    if not st.session_state.searching and flight_options is not None:
        if isinstance(flight_options, dict) and "error" in flight_options:
            st.error(flight_options["error"])
        else:
            st.write("Flight Options")
            st.dataframe(flight_options, width='stretch')
