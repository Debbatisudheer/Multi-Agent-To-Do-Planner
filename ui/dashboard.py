# ui/dashboard.py

import streamlit as st
import requests
import websocket
import threading
import json

# ⚠️ Change this when running locally (localhost:8000)
# BACKEND_URL = "http://localhost:8000"
BACKEND_URL = "https://multi-agent-to-do-planner.onrender.com"  # Render backend URL


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

if is_online:
    st.markdown(
        "<div style='background:#d4f8d4;padding:8px 12px;border-radius:8px;width:fit-content;'>"
        "🟢 Using GPT Autonomy (Online Mode)</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div style='background:#ffe3e3;padding:8px 12px;border-radius:8px;width:fit-content;'>"
        "🔌 Offline Mode (No GPT Key)</div>",
        unsafe_allow_html=True,
    )


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
        ws.connect("wss://multi-agent-to-do-planner.onrender.com/ws/")  # ✅ notice the '/' at the end
        # ws.connect("ws://localhost:8000/ws/")  # use this when testing locally

        while True:
            message = ws.recv()

            # Backend sends plain text, so handle both formats
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

    # Start websocket listener thread
    thread = threading.Thread(target=ws_listener, daemon=True)
    thread.start()

    timeline.write("⚙️ Starting agent...")

    try:
        response = requests.post(
            f"{BACKEND_URL}/run-agent",
            json={"goal": goal},
            timeout=30
        ).json()

        output_box.success("✅ Completed!")
        st.subheader("🧠 Final Result:")
        st.write(response.get("final", "No final result received."))

    except Exception as e:
        output_box.error(f"❌ Error communicating with backend: {e}")
