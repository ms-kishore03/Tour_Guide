import streamlit as st
from utils import init_session_state, logout
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import Utilities.databaseManager as databaseManager

init_session_state()
st.set_page_config(page_title="Home", page_icon="🏠", layout="centered")

if not st.session_state.user:
    st.switch_page("Login_Register.py")

# ---- Custom Styling ----
st.markdown("""
    <style>
    h1 {
        text-align: center;
        margin-bottom: 0.3em;
    }
    .subtitle {
        text-align: center;
        color: #b0b0b0;
        margin-bottom: 2em;
        font-size: 1.05rem;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2.5rem;
    }
    .trip-card {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        border: 1px solid #2c2c2c;
        cursor: pointer;
    }
    .trip-card:hover {
        background-color: #2a2a2a;
        border-color: #00b4d8;
        transform: translateY(-2px);
    }
    .trip-title {
        font-weight: 600;
        color: white;
        font-size: 1.05rem;
        margin-bottom: 0.2rem;
    }
    .trip-meta {
        font-size: 0.9rem;
        color: #aaaaaa;
    }
    .trip-desc {
        font-size: 0.88rem;
        color: #c5c5c5;
        margin-top: 0.3rem;
        line-height: 1.3em;
    }
    a.trip-link {
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown(f"<h1>🏠 Welcome, {st.session_state.user}!</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your next adventure </p>', unsafe_allow_html=True)

# ---- Top Buttons ----
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    if st.button(" Explore Trips", use_container_width=True):
        st.switch_page("pages/Trip_Planner.py")
with col2:
    if st.button("Logout", use_container_width=True):
        logout()
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.subheader("📚 Your Saved Trips")

# ---- Clickable HTML Cards ----

saved_trips = databaseManager.get_saved_trips()

if saved_trips:
    for i, trip in enumerate(saved_trips, start=1):
        place = trip.get("Place Name", f"Trip {i}")
        scenario = trip.get("Scenario", "Adventure")
        description = trip.get("Description", "No description available")

        with st.container():
            if st.button(f"{i}. {place} ✨ {scenario}", key=f"trip_{i}", use_container_width=True):
                st.session_state.current_trip = trip
                st.switch_page("pages/Trip_Overview.py")

            st.markdown(
                f"<div class='trip-desc'>{description}</div>",
                unsafe_allow_html=True
            )
else:
    st.info("Explore and save trips to see them listed here.")
