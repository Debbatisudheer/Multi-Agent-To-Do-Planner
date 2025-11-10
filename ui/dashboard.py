# ui/dashboard.py

import streamlit as st
import requests
import websocket
import threading
import json

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Multi-Agent Task Planner", page_icon="🤖")
st.title("🤖 Multi-Agent Task Planner")

# ----------------------------------------------------
# ✅ Detect Online / Offline Mode
# ----------------------------------------------------
try:
    status = requests.get(f"{BACKEND_URL}/status").json()
    is_online = status["mode"] == "online"
except Exception:
    is_online = False

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

# ✅ Space for timeline and final output
timeline = st.container()
output_box = st.empty()


# ----------------------------------------------------
# ✅ WebSocket Listener (Fixed JSON decode issue)
# ----------------------------------------------------
def ws_listener():
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:8000/ws")

    while True:
        message = ws.recv()

        # Try to parse JSON (backend sends plain text)
        try:
            data = json.loads(message)
            log = data.get("log", message)
        except:
            log = message  # fallback to plain text

        # update live logs on UI
        timeline.write(f"🔹 {log}")


# ----------------------------------------------------
# ✅ Run Agent Button
# ----------------------------------------------------
if st.button("Run Agent"):

    # Start websocket listener in background
    thread = threading.Thread(target=ws_listener, daemon=True)
    thread.start()

    timeline.write("⚙️ Starting agent...")

    # POST call to backend
    response = requests.post(
        f"{BACKEND_URL}/run-agent",
        json={"goal": goal}
    ).json()

    # Display final result
    output_box.success("✅ Completed!")
    st.subheader("🧠 Final Result")
    st.write(response["final"])
