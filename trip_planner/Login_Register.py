import streamlit as st
from utils import init_session_state
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Utilities.User_Authentication as User_Authentication

st.set_page_config(
    page_title="Trip Planner",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

init_session_state()

# If already logged in → go to Home directly
if st.session_state.user:
    st.switch_page("pages/Home.py")

st.title("🔐 Welcome to Trip Planner")

tab1, tab2 = st.tabs(["Login", "Register"])

# ---------- LOGIN ----------
with tab1:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            login_success = User_Authentication.login(username, password)
            if not login_success:
                st.error("Invalid username or password.")
            else:
                st.session_state.user = username
                st.success(f"Welcome back, {username}!")
                st.switch_page("pages/Home.py")
        else:
            st.error("Please enter both username and password.")

# ---------- REGISTER ----------
with tab2:
    st.subheader("Register New Account")
    new_username = st.text_input("Choose Username")
    new_password = st.text_input("Choose Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email Address")

    if st.button("Register"):
        if not new_username or not new_password:
            st.error("All fields are required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            registration_result = User_Authentication.register(new_username, new_password, confirm_password, email)
            if registration_result != "User registered successfully!":
                st.error(registration_result)
            else:
                st.session_state.user = new_username
                st.success("Account created! Redirecting...")
                st.switch_page("pages/Home.py")
