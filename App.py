import streamlit as st
import pandas as pd

# Initialize session state
if 'saved_trips' not in st.session_state:
    st.session_state.saved_trips = []
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = None

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        text-align: center;
        color: #4CAF50;
    }
    .sub-header {
        font-size: 1.5em;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# If already logged in, redirect to home
if st.session_state.user:
    st.switch_page("pages/home.py")

st.markdown('<h1 class="main-header"></h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        if username and password:
            st.success("Logged in successfully!")
            st.session_state.user = username  # Simulate login
            st.rerun()
        else:
            st.error("Please enter username and password.")

with tab2:
    st.subheader("Register")
    reg_username = st.text_input("Username", key="reg_username")
    reg_password = st.text_input("Password", type="password", key="reg_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    email = st.text_input("Email", key="email")
    if st.button("Register"):
        if reg_username and reg_password and confirm_password and email:
            if reg_password == confirm_password:
                st.success("Registered successfully!")
                st.session_state.user = reg_username
                st.rerun()
            else:
                st.error("Passwords do not match.")
        else:
            st.error("Please fill all fields.")