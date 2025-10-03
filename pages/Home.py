import streamlit as st
import pandas as pd

# Check if logged in
if 'user' not in st.session_state or not st.session_state.user:
    st.warning("Please log in to access the Home page.")
    st.switch_page("app.py")
    st.stop()

st.markdown('<h1 class="main-header">Welcome Home!</h1>', unsafe_allow_html=True)
st.markdown(f"<h2 class='sub-header'>Welcome, {st.session_state.user}!</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Explore"):
        st.switch_page("pages/explore.py")
with col2:
    if st.button("Create a Trip Plan"):
        st.switch_page("pages/explore.py")
with col3:
    if st.button("Logout"):
        del st.session_state.user
        if 'current_trip' in st.session_state:
            del st.session_state.current_trip
        st.switch_page("app.py")

st.subheader("History / Saved Plans")
if st.session_state.saved_trips:
    df = pd.DataFrame(st.session_state.saved_trips)
    st.dataframe(df)
else:
    st.info("No history yet. Start exploring!")