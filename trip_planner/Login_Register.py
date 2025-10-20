import streamlit as st
from streamlit.components.v1 import html
from utils import init_session_state
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Utilities.User_Authentication as User_Authentication

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(
    page_title="Trip Planner",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

init_session_state()

# Redirect if already logged in
if st.session_state.user:
    st.switch_page("pages/Home.py")

st.title("🔐 Welcome to Trip Planner")

# -----------------------------
# Session flags
# -----------------------------
if "reset_register_form" not in st.session_state:
    st.session_state.reset_register_form = False
if "switch_to_login" not in st.session_state:
    st.session_state.switch_to_login = False

# -----------------------------
# Helper function: Safe tab switch using JS
# -----------------------------
def switch_tab(tab_index: int):
    js_code = f"""
    <script>
    const tabGroups = window.parent.document.querySelectorAll('[data-baseweb="tab-list"]');
    if (tabGroups.length > 0) {{
        const buttons = tabGroups[0].querySelectorAll('button');
        if (buttons[{tab_index}]) {{
            buttons[{tab_index}].click();
        }}
    }}
    </script>
    """
    html(js_code, height=0)

# -----------------------------
# Reset form if flag is set
# -----------------------------
if st.session_state.reset_register_form:
    for key in ["new_username", "new_password", "confirm_password", "email"]:
        st.session_state[key] = ""
    st.session_state.reset_register_form = False

# -----------------------------
# Tabs
# -----------------------------
login_tab, register_tab = st.tabs(["Login", "Register"])

# ---------- LOGIN ----------
with login_tab:
    st.subheader("Login to Your Account")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")

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
with register_tab:
    st.subheader("Create a New Account")
    
    new_username = st.text_input("Choose Username", key="new_username")
    new_password = st.text_input("Choose Password", type="password", key="new_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    email = st.text_input("Email Address", key="email")

    if st.button("Register"):
        if not new_username or not new_password:
            st.error("All fields are required.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            registration_result = User_Authentication.register(
                new_username, new_password, confirm_password, email
            )
            if registration_result != "User registered successfully!":
                st.error(registration_result)
            else:
                st.success("✅ Account created successfully! Redirecting to login...")

                # Set flags to reset form and switch tab on next render
                st.session_state.reset_register_form = True
                st.session_state.switch_to_login = True

                # Force rerun to clear form
                st.rerun()

# -----------------------------
# Switch to login tab if flag is set
# -----------------------------
if st.session_state.switch_to_login:
    switch_tab(0)
    st.session_state.switch_to_login = False