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
        "searching": False,
        "chat_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def logout():
    # List all session variables you want cleared on logout
    keys_to_clear = [
        "user",
        "saved_trips",
        "current_trip",
        "trip_preferences",
        "destination_suggestions",
        "explore_step",
        "scenario",
        "activity",
        "climate",
        "chat_history",
        "weather_info",
        "searching",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Redirect to login/register page
    st.switch_page("Login_Register.py")
    st.stop()
