import streamlit as st

def init_session_state():
    defaults = {
        "user": None,
        "saved_trips": [],
        "current_trip": None,
        "trip_preferences": {},
        "destination_suggestions": [],
        "explore_step": 1,
        "scenario": None,
        "activity": "",
        "climate": "No Preference",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def logout():
    st.session_state.user = None
    st.session_state.explore_step = 1
    st.session_state.trip_preferences = {}
    st.session_state.destination_suggestions = []
    st.session_state.current_trip = None
    st.switch_page("Login_Register.py")
    st.stop()
