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
        st.session_state["planner_mode"] = "travel"
        st.info("Travel planning mode activated!")
        st.switch_page("pages/Flight_Search.py")

with col2:
    st.subheader("🏨 Need help with accommodations?")
    st.write("Find suitable stays or hotel recommendations.")
    if st.button("Find Stays", key="stay_help"):
        st.session_state["planner_mode"] = "stay"
        st.info("Accommodation planning mode activated!")

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

# ----------------- MAIN PLANNING LAYOUT -----------------
chat_col, itinerary_col = st.columns([2, 1])

# --- Chatbot Section ---
with chat_col:
    st.subheader("💬 Travel Planning Assistant")
    st.write("Chat with the assistant to create or modify your itinerary, ask travel questions, or get recommendations.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", placeholder="e.g., Plan a 3-day itinerary for Tokyo.")
        send = st.form_submit_button("Send")

    if send and user_input:
        conversation_history = st.session_state["chat_history"]
        conversation_history.append({"role": "user", "content": user_input})
        response = agents.enquiry_agent_chatbot(
            conversation_history, user_input, st.session_state.get("weather_info", "")
        )
        conversation_history.append({"role": "assistant", "content": response})
        st.session_state["chat_history"] = conversation_history

    # Display chat messages
    for message in st.session_state["chat_history"]:
        role = message["role"]
        if role == "user":
            st.chat_message("user").markdown(message["content"])
        else:
            st.chat_message("assistant").markdown(message["content"])

# --- Itinerary Section ---
with itinerary_col:
    st.subheader("🗓️ Itinerary List")
    st.write("View or edit your travel plan here.")

    if "itinerary_list" not in st.session_state:
        st.session_state["itinerary_list"] = []

    for idx, item in enumerate(st.session_state["itinerary_list"], start=1):
        st.markdown(f"**{idx}.** {item}")

    st.markdown("---")
    new_item = st.text_input("Add to itinerary:", key="new_itinerary_item", placeholder="e.g., Visit Eiffel Tower")
    if st.button("Add Itinerary Item"):
        if new_item.strip():
            st.session_state["itinerary_list"].append(new_item.strip())
            st.success("Itinerary item added!")

left, center, right = st.columns([1, 1, 1])

with center:
    st.button("Start Trip")