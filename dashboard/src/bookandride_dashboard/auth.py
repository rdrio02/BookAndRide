import streamlit as st
from api_client import login, register, get_me


def login_page():
    st.header("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            data = login(email, password)
            st.session_state.token = data["access_token"]

            user = get_me(st.session_state.token)
            st.session_state.user = user
            st.session_state.authenticated = True

            st.success("Logged in successfully!")
            st.rerun()

        except Exception as e:
            st.error("Invalid email or password")


def register_page():
    st.header("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm:
            st.error("Passwords do not match")
            return

        try:
            register(email, password)
            st.success("Account created! You can now log in.")
        except Exception as e:
            st.error("Registration failed (email may already exist)")
