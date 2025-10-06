import streamlit as st
from utils import init_session_state, logout

init_session_state()
st.set_page_config(page_title="Home", page_icon="🏠", layout="centered")

if not st.session_state.user:
    st.switch_page("Login_Register.py")

st.title(f"🏠 Welcome, {st.session_state.user}!")
st.markdown("Plan your next adventure 🌍")

col1, col2 = st.columns(2)
with col1:
    if st.button("🌎 Explore Trips"):
        st.switch_page("pages/Explore.py")
with col2:
    if st.button("📤 Logout"):
        logout()

st.divider()
st.subheader("📚 Your Saved Trips")

if st.session_state.saved_trips:
    for i, trip in enumerate(st.session_state.saved_trips, start=1):
        st.markdown(f"**{i}. {trip['Place Name']}** — {trip.get('Scenario','')}")
        if st.button(f"View {trip['Place Name']}", key=f"view_{i}"):
            st.session_state.current_trip = trip
            st.switch_page("pages/Trip_Overview.py")
else:
    st.info("No trips saved yet. Start exploring!")
