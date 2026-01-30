# dashboard.py
import streamlit as st
from api_client import start_rental, stop_rental

def dashboard_page():
    st.header("🚲 Bike Rental")

    user = st.session_state.user
    st.info(f"Logged in as **{user['email']}**")

    # Store rentals in session
    if "rentals" not in st.session_state:
        st.session_state.rentals = []

    col1, col2 = st.columns([1, 2])

    # ------------------
    # LEFT: Start rental
    # ------------------
    with col1:
        st.subheader("Start a rental")

        bike_id = st.text_input("Bike ID", value="BIKE-001")

        if st.button("▶ Start Rental"):
            result = start_rental(user_id=user["id"], bike_id=bike_id)

            st.session_state.rentals.append({
                "rental_id": result["rental_id"],
                "bike_id": bike_id,
                "status": "active",
                "data": result
            })

            st.success("Rental started!")

    # ------------------
    # RIGHT: Active / past rentals
    # ------------------
    with col2:
        st.subheader("Your rentals")

        if not st.session_state.rentals:
            st.write("No rentals yet.")
            return

        for rental in st.session_state.rentals:
            with st.container(border=True):
                st.write(f"🚲 **Bike:** {rental['bike_id']}")
                st.write(f"🆔 **Rental ID:** `{rental['rental_id']}`")

                if rental["status"] == "active":
                    st.write("⏱ **Status:** Active")

                    if st.button(
                        "⏹ Stop rental",
                        key=f"stop_{rental['rental_id']}"
                    ):
                        result = stop_rental(rental["rental_id"])
                        rental["status"] = "stopped"
                        rental["data"] = result
                        st.rerun()

                else:
                    st.write("✅ **Status:** Finished")

                    price = rental["data"].get("price_eur")
                    duration = rental["data"].get("duration_min")

                    if price is not None:
                        st.write(f"💰 **Price:** €{price}")

                    if duration is not None:
                        st.write(f"⏱ **Duration:** {duration} min")
