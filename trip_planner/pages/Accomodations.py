import os
import sys
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from API_Handlers import AccomodationHandler

st.set_page_config(page_title="Accommodation Finder", page_icon="🏨", layout="centered")

st.title("🏨 Find Your Perfect Stay")

with st.form("accommodation_search"):
    st.subheader("Search for Stays")
    location = st.text_input("Location", placeholder="Enter destination")
    checkin = st.date_input("Check-in Date")
    checkout = st.date_input("Check-out Date")
    submitted = st.form_submit_button("Search Accommodations")

if "searching" not in st.session_state:
    st.session_state.searching = False

if submitted:
    st.session_state.searching = True

    if st.session_state.searching:
        status_placeholder = st.empty()
        status_placeholder.success("Searching for accommodations... 🏨")

        try:
            accommodations = AccomodationHandler.get_accomodations(
                location, checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d")
            )

            if accommodations:
                st.session_state.searching = False
                status_placeholder.empty()
                st.subheader("Top Accommodation Options:")
                for idx, name in enumerate(accommodations, start=1):
                    st.markdown(f"{idx}. {name}")
            else:
                st.warning("No accommodations found for the given criteria.")
        except Exception as e:
            st.error(f"An error occurred while searching for accommodations: {e}")
        