import streamlit as st
import Utilities.agents as agents
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from Utilities import databaseManager
from API_Handlers import geoapify
from cognix_ai.cognix_ai import cognix_ai
from cognix_ai.cognix_ai import collection



st.set_page_config(page_title="Plan Your Trip", page_icon="🗺️", layout="wide")



user = st.session_state.get("user")
trip = st.session_state.get("current_trip")
place = trip.get("Place Name", "") if trip else ""

st.title(f"🚀 Trip Planning Dashboard - {place}")

if "attractive_cache" not in st.session_state:
    st.session_state["attractive_cache"] = {}

if place and place not in st.session_state["attractive_cache"]:
    st.session_state["attractive_cache"][place] = geoapify.geoapify_attractions(place)

attractive_points = st.session_state["attractive_cache"].get(place, [])
# ----------------- TOP BUTTON ROW -----------------
col1, col2, col3 = st.columns(3)

#--------------------flight booking section---------------------

with col1:
    st.subheader("✈️ Need help with travel plans?")
    st.write("Get route suggestions, flight info, or transport options.")
    if st.button("Plan Travel", key="travel_help"):
        st.switch_page("pages/Flight_Search.py")

#--------------------accommodation section---------------------
with col2:
    st.subheader("🏨 Need help with accommodations?")
    st.write("Find suitable stays or hotel recommendations.")
    if st.button("Find Stays", key="stay_help"):
        st.switch_page("pages/Accomodations.py")

#--------------------todo list section---------------------
with col3:

    st.subheader("📝 View To-Do List")
    # decide place vs global
    todo_key = place or "__global_todo__"
    user = st.session_state.get("user")

    if not user:
        st.warning("User not set")
        st.stop()

    # init session cache
    if "todo_list" not in st.session_state:
        st.session_state["todo_list"] = {}  # a dictionary to store the todo list for each place

    # load from DB only once per place
    if todo_key not in st.session_state["todo_list"]:
        st.session_state["todo_list"][todo_key] = databaseManager.get_todo(
            user, todo_key
        )

    list_to_do = st.session_state["todo_list"][todo_key] # datatype: list

    # input
    new_task = st.text_input(
        "Add a new task:",
        key=f"todo_input_{todo_key}",
        placeholder="e.g., Book tickets"
    )

    # add task
    if st.button("Add Task", key=f"add_btn_{todo_key}"):
        task = new_task.strip()
        if task and task not in list_to_do:
            list_to_do.append(task)
            databaseManager.add_todo(user, todo_key, task)
            st.rerun()

    # render
    if list_to_do:
        st.markdown("**Your tasks:**")
        for task in list_to_do:
            st.markdown(f"- {task}") 
st.divider()

# ----------------- MAIN PLANNING LAYOUT -----------------
chat_col, itinerary_col = st.columns([2, 1])

# --- Chatbot Section ---
with chat_col:
    st.subheader("💬 Travel Planning Assistant")
    st.write("Chat with the assistant to create or modify your itinerary, ask travel questions, or get recommendations.")

    # ---- CHAT MEMORY (PLACE-AWARE) ----
    if "chat_histories" not in st.session_state:
        st.session_state["chat_histories"] = {}

    chat_key = place if place else "__global_planning__"

    if chat_key not in st.session_state["chat_histories"]:
        st.session_state["chat_histories"][chat_key] = []

    chat_history = st.session_state["chat_histories"][chat_key]


    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", placeholder="e.g., Plan a 3-day itinerary for Tokyo.")
        send = st.form_submit_button("Send")

    if send and user_input:
        chat_history.append({"role": "user", "content": user_input})

        response = cognix_ai(
            user_input=user_input,
            username=st.session_state.get("user", "guest"),
            conversation_history=chat_history,
            place=place,
            weather_data = st.session_state.get("weather_info", ""),
            geoapify_data=st.session_state.get('geoapify_data', [])
        )

        chat_history.append({"role": "assistant", "content": response})

    # ---- DISPLAY CHAT ----
    for message in reversed(chat_history):
        st.chat_message(message["role"]).markdown(message["content"])

# --- Itinerary Section ---

# --- Itinerary Section (DB-backed, read-only) ---
with itinerary_col:
    st.subheader("🗓️ Your Itinerary")

    username = st.session_state.get("user", "guest")

    itinerary_items = databaseManager.get_itinerary_from_db(
        collection=collection,
        username=username,
        place=place
    )

    if not itinerary_items:
        st.info("No itinerary finalized yet. Start planning in the chat 👉")
    else:
        for idx, item in enumerate(itinerary_items, start=1):
            location = item.get("location", "Unknown place")
            date = item.get("date", "unknown")
            time = item.get("time", "unknown")

            st.markdown(
                f"""
                **{idx}. {location}**  
                🗓️ {date} &nbsp;&nbsp; ⏰ {time}
                """
            )

left, center, right = st.columns([1, 1, 1])

with center:
    if st.button("Start Trip"):
        res = databaseManager.get_ongoing_trip(user)
        if res:
            st.warning("You already have an ongoing trip. Please complete or cancel it before starting a new one.")
            st.stop()
        else:
            databaseManager.save_ongoing_trips(username=user, place=place)
            st.success("Trip started! Navigate to the 'Ongoing Trips' page to manage your trip.")
            st.switch_page("pages/Ongoing_Trips.py")