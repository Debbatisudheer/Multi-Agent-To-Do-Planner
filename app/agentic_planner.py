# app/agentic_planner.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool

from app.websocket_manager import websocket_manager
from app.agents.flight_agent import agent as flight_agent
from app.agents.reminder_agent import agent as reminder_agent
from app.agents.email_agent import agent as email_agent

load_dotenv()

# -------------------------------------------------------
# Tools
# -------------------------------------------------------

@tool
def read_emails() -> dict:
    """Reads emails and extracts tasks"""
    task = type("Task", (), {"id": "lc", "kind": "read_emails", "payload": {}})
    result = email_agent.run(task)
    return result.model_dump()

@tool
def book_flight(origin: str, dest: str, date: str) -> dict:
    """Books a mock flight"""
    task = type("Task", (), {
        "id": "lc",
        "kind": "book_flight",
        "payload": {"origin": origin, "dest": dest, "date": date}
    })
    result = flight_agent.run(task)
    return result.model_dump()

@tool
def schedule_reminder(time: str, note: str = "Reminder") -> dict:
    """Schedules a reminder"""
    task = type("Task", (), {
        "id": "lc",
        "kind": "schedule_reminder",
        "payload": {"time": time, "note": note}
    })
    result = reminder_agent.run(task)
    return result.model_dump()


SYSTEM = """
You are an autonomous Multi-Agent Planner.
Use tools only when needed. Never explain reasoning.
"""

api_key = os.getenv("OPENAI_API_KEY")
llm = None

if api_key:
    llm = ChatOpenAI(
        model="gpt-4.1-mini",
        temperature=0,
    ).bind_tools([read_emails, book_flight, schedule_reminder])


# -------------------------------------------------------
# ✅ ASYNC version (supports WebSocket awaits)
# -------------------------------------------------------

async def run_agent(goal: str):

    # OFFLINE MODE (no GPT key)
    if not api_key:
        await websocket_manager.broadcast("🔌 Offline mode — fallback rules")

        if "email" in goal.lower():
            await websocket_manager.broadcast("📧 Reading emails (offline)…")
            read_emails.invoke({})
            await websocket_manager.broadcast("✅ Emails done")
            return "(offline) ✓ Emails processed", []

        if "flight" in goal.lower():
            await websocket_manager.broadcast("✈️ Booking flight (offline)…")
            book_flight.invoke({"origin": "HYD", "dest": "BLR", "date": "2025-11-25"})
            await websocket_manager.broadcast("✅ Flight booked")
            return "(offline) ✓ Flight booked", []

        return "(offline mode) Could not understand", []


    # ONLINE MODE
    await websocket_manager.broadcast(f"🤖 Starting Agent (online) — Goal: {goal}")

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": goal},
    ]

    logs = []

    while True:
        response = llm.invoke(messages)

        await websocket_manager.broadcast(f"🟡 GPT tool decision: {response.tool_calls}")

        if not response.tool_calls:
            await websocket_manager.broadcast("🎉 Completed")
            await websocket_manager.broadcast(f"🧠 Final: {response.content}")
            return response.content, logs

        messages.append({"role": "assistant", "content": "", "tool_calls": response.tool_calls})

        for call in response.tool_calls:
            tool_name = call["name"]
            args = call["args"]
            call_id = call["id"]

            await websocket_manager.broadcast(f"⚙️ Executing: {tool_name}")

            if tool_name == "read_emails":
                result = read_emails.invoke({})
                await websocket_manager.broadcast("📧 Reading emails…")

            elif tool_name == "book_flight":
                result = book_flight.invoke(args)
                await websocket_manager.broadcast("✈️ Booking flight…")

            elif tool_name == "schedule_reminder":
                result = schedule_reminder.invoke(args)
                await websocket_manager.broadcast("⏰ Scheduling reminder…")

            await websocket_manager.broadcast(f"✅ {tool_name} completed")

            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": str(result),
            })
