import streamlit as st
import sys, os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from Utilities import databaseManager
from cognix_ai.cognix_ai import collection

st.set_page_config(page_title="Ongoing Trips", page_icon="🧳", layout="wide")

# -------------------- USER + TRIP GUARD --------------------
user = st.session_state.get("user")

if not user:
    st.error("User not logged in.")
    st.stop()

ongoing_trip_data = databaseManager.get_ongoing_trip(user)

if not ongoing_trip_data:
    st.warning("No ongoing trip found. Please start a trip from the Trip Planner page.")
    st.stop()

place = ongoing_trip_data.get("place")
trip_details = ongoing_trip_data.get("trip_details", {})
existing_expenses = databaseManager.get_expenses(user,place)


# -------------------- SESSION STATE INIT --------------------
if "expenses" not in st.session_state:
    st.session_state["expenses"] = existing_expenses.copy()

# -------------------- PAGE TITLE --------------------
st.title(f"Enjoy your Vacation to {place}, {user}")

left, right = st.columns([1, 1])

# -------------------- LEFT COLUMN --------------------
with left:
    st.markdown("### Trip Details")
    st.markdown(f"""
    - **Destination**: {trip_details.get('Place Name', 'N/A')}
    - **Scenario**: {trip_details.get('Scenario', 'N/A')}
    - **Duration**: {trip_details.get('Duration', 'N/A')}
    - **Climate**: {trip_details.get('Climate', 'N/A')}
    - **People**: {trip_details.get('People', 'N/A')}
    - **Transport**: {trip_details.get('Transport', 'N/A')}
    - **Description**: {trip_details.get('Description', 'No description available')}
    """)

    st.subheader("Your Itinerary List")

    itinerary_items = databaseManager.get_itinerary_from_db(
        collection=collection,
        username=user,
        place=place
    )

    if itinerary_items:
        for idx, item in enumerate(itinerary_items, start=1):
            location = item.get("location", "Unknown place")
            date = item.get("date", "Unknown")
            time = item.get("time", "Unknown")

            st.markdown(
                f"""
                **{idx}. {location}**  
                🗓️ {date} &nbsp;&nbsp; ⏰ {time}
                """
            )
    else:
        st.info("No itinerary items added yet.")

# -------------------- RIGHT COLUMN --------------------
with right:
    st.subheader("Provide your expenses on your trip here:")

    expense = st.text_input("Enter your expense amount:")

    category = st.selectbox(
        "Select expense category:",
        ["Food", "Accommodation", "Transport", "Activities", "Miscellaneous"]
    )

    date = st.date_input("Select date of expense:")

    if st.button("Add Expense"):
        new_expense = {
            "amount": float(expense),
            "category": category,
            "Date": datetime.combine(date, datetime.min.time())
        }

        st.session_state["expenses"].append(new_expense)

        databaseManager.save_expenses(
            user,
            place,
            st.session_state["expenses"]
        )

    # -------------------- EXPENSE TABLE --------------------
    expenses = st.session_state.get("expenses", [])
    expense_df = pd.DataFrame(expenses)

    if not expense_df.empty:
        expense_df.index = range(1, len(expense_df) + 1)
        expense_df.index.name = "No."

        st.subheader("Expense Log")
        st.table(expense_df)

        # -------------------- ANALYSIS --------------------
        st.subheader("Analysis of your Expenses")

        st.markdown("Expenses per category:")
        per_category_grp = (
            expense_df.groupby("category")["amount"]
            .sum()
            .reset_index()
        )
        per_category_grp.columns = ["Category", "Total Amount"]
        per_category_grp.index = range(1,len(per_category_grp)+1)
        st.table(per_category_grp)

        st.markdown("Expenses per day:")
        per_day_grp = (
            expense_df.groupby("Date")["amount"]
            .sum()
            .reset_index()
        )
        per_day_grp.columns = ["Date", "Total Amount"]
        per_day_grp.index = range(1,len(per_day_grp)+1)
        st.table(per_day_grp)

    else:
        st.info("No expenses added yet.")

# -------------------- END TRIP --------------------
_, center, _ = st.columns([1, 1, 1])

with center:
    if st.button("End Trip"):
        databaseManager.end_ongoing_trip(user, place)
        st.success("Trip ended! You can start a new trip from the Trip Planner page.")
        st.switch_page("pages/Trip_Planner.py")
