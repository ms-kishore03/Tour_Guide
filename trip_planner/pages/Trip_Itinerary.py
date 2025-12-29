import streamlit as st
import agents

st.set_page_config(page_title="Plan Your Trip", page_icon="🗺️", layout="wide")

st.title("🚀 Trip Planning Dashboard")

# ----------------- TOP BUTTON ROW -----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("✈️ Need help with travel plans?")
    st.write("Get route suggestions, flight info, or transport options.")
    if st.button("Plan Travel", key="travel_help"):
        st.switch_page("pages/Flight_Search.py")

with col2:
    st.subheader("🏨 Need help with accommodations?")
    st.write("Find suitable stays or hotel recommendations.")
    if st.button("Find Stays", key="stay_help"):
        st.switch_page("pages/Accomodations.py")

with col3:
    st.subheader("📝 To-Do List")
    if "todo_list" not in st.session_state:
        st.session_state["todo_list"] = []
    new_task = st.text_input("Add a new task:", key="todo_input", placeholder="e.g., Book tickets")
    if st.button("Add Task"):
        if new_task.strip():
            st.session_state["todo_list"].append(new_task.strip())
            st.success("Task added!")
    if st.session_state["todo_list"]:
        st.markdown("**Your tasks:**")
        for task in st.session_state["todo_list"]:
            st.markdown(f"- {task}")

st.divider()

trip = st.session_state.get("current_trip")
place = trip.get("Place Name", "") if trip else ""

if "attractive_cache" not in st.session_state:
    st.session_state["attractive_cache"] = {}

if place and place not in st.session_state["attractive_cache"]:
    st.session_state["attractive_cache"][place] = agents.get_attractive_points(place)

attractive_points = st.session_state["attractive_cache"].get(place, [])


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

        response = agents.enquiry_agent_chatbot(
            chat_history,
            user_input,
            st.session_state.get("weather_info", ""),
            place,
            attractive_points,
        )

        chat_history.append({"role": "assistant", "content": response})

    # ---- DISPLAY CHAT ----
    for message in chat_history:
        st.chat_message(message["role"]).markdown(message["content"])

# --- Itinerary Section ---
with itinerary_col:
    st.subheader("🗓️ Itinerary List")
    st.write("View or edit your travel plan here.")

    if "itineraries" not in st.session_state:
        st.session_state["itineraries"] = {}

    itinerary_key = place if place else "__global_planning__"

    if itinerary_key not in st.session_state["itineraries"]:
        st.session_state["itineraries"][itinerary_key] = []

    itinerary_list = st.session_state["itineraries"][itinerary_key]

    # ---- DISPLAY ITINERARY ----
    for idx, item in enumerate(itinerary_list, start=1):
        st.markdown(f"**{idx}.** {item}")

    st.markdown("---")

    new_item = st.text_input(
        "Add to itinerary:",
        key=f"new_itinerary_item_{itinerary_key}",
        placeholder="e.g., Visit Eiffel Tower",
    )

    if st.button("Add Itinerary Item", key=f"add_itinerary_{itinerary_key}"):
        if new_item.strip():
            itinerary_list.append(new_item.strip())
            st.success("Itinerary item added!")


left, center, right = st.columns([1, 1, 1])

with center:
    st.button("Start Trip")