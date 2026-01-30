# app.py
import os
import streamlit as st

from auth import login_page, register_page
from utils import test_api_connection
from dashboard import dashboard_page

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(
    page_title="Book & Ride Dashboard",
    layout="centered",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://nginx")

# SESSION DEFAULTS
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None

# LOGOUT
def logout():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()


# MAIN ROUTING
if not st.session_state.authenticated:
    page = st.sidebar.radio("Account", ["Login", "Register"])

    if page == "Login":
        login_page()
    else:
        register_page()

else:
    st.sidebar.success(f"Logged in as {st.session_state.user['email']}")
    st.sidebar.button("Logout", on_click=logout)

    st.title("Dashboard")
    dashboard_page()
