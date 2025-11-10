# ui/dashboard.py

import streamlit as st
import requests
import websocket
import threading
import json


# ⚠️ Change for local testing:  http://localhost:8000
BACKEND_URL = "https://multi-agent-to-do-planner.onrender.com"


st.set_page_config(page_title="Multi-Agent Task Planner", page_icon="🤖")
st.title("🤖 Multi-Agent Task Planner")


# ----------------------------------------------------
# ✅ Detect Online / Offline Mode
# ----------------------------------------------------
def check_status():
    try:
        status = requests.get(f"{BACKEND_URL}/status", timeout=5).json()
        return status["mode"] == "online"
    except Exception:
        return False


is_online = check_status()


# ✅ Style for visible badges
badge_style = """
<style>
.status-badge {
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    display: inline-block;
    color: black !important;
}
.online {
    background-color: #b7f5b7;
}
.offline {
    background-color: #ffb3b3;
}
</style>
"""

st.markdown(badge_style, unsafe_allow_html=True)

if is_online:
    st.markdown("<div class='status-badge online'>🟢 Using GPT Autonomy (Online Mode)</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='status-badge offline'>🔌 Offline Mode (No GPT Key)</div>", unsafe_allow_html=True)


st.write("""
💡 **What can I do?**
📧 Read emails and extract tasks  
✈️ Book flights (origin, destination, date)  
⏰ Schedule reminders  

### ✍️ Example goals
- `Read my emails and book a flight`
- `Book a flight from HYD to BLR on 2025-11-25`
- `Set reminder tomorrow at 6 PM`
""")

goal = st.text_input("🔽 Type your goal")


# ----------------------------------------------------
# ✅ UI Containers for Progress + Final Output
# ----------------------------------------------------
timeline = st.container()
output_box = st.empty()


# ----------------------------------------------------
# ✅ WebSocket Listener
# ----------------------------------------------------
def ws_listener():
    try:
        ws = websocket.WebSocket()

        # Use /ws/ (Render requires trailing slash)
        ws.connect("wss://multi-agent-to-do-planner.onrender.com/ws/")

        while True:
            message = ws.recv()

            # Backend may send plain text; handle both
            try:
                data = json.loads(message)
                log = data.get("log", message)
            except json.JSONDecodeError:
                log = message

            timeline.write(f"🔹 {log}")

    except Exception as e:
        timeline.write(f"❌ WebSocket error: {e}")


# ----------------------------------------------------
# ✅ Run Agent Button
# ----------------------------------------------------
if st.button("Run Agent"):

    if not goal.strip():
        st.warning("⚠️ Please enter a goal before running the agent.")
        st.stop()

    # Start WebSocket listener thread
    thread = threading.Thread(target=ws_listener, daemon=True)
    thread.start()

    timeline.write("⚙️ Starting agent...")

    try:
        response = requests.post(
            f"{BACKEND_URL}/run-agent",
            json={"goal": goal},
            timeout=60,
        ).json()

        output = response.get("final", "❌ No final result received.")
        output_box.success("✅ Completed!")
        st.subheader("🧠 Final Result:")
        st.write(output)

    except Exception as e:
        output_box.error(f"❌ Error communicating with backend: {e}")
