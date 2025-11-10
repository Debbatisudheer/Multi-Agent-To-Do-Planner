# api/server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.agentic_planner import run_agent
from app.websocket_manager import websocket_manager

app = FastAPI()

# Allow UI (Streamlit) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GoalRequest(BaseModel):
    goal: str


# ------------------------------------------------------
# ✅ Status API (to show online/offline mode on UI)
# ------------------------------------------------------
@app.get("/status")
def get_status():
    from app.agentic_planner import api_key
    return {"mode": "online" if api_key else "offline"}


# ------------------------------------------------------
# ✅ WebSocket route for streaming progress logs
# ------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()  # Just keep the connection open
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


# ------------------------------------------------------
# ✅ RUN AGENT (ASYNC)
# ------------------------------------------------------
@app.post("/run-agent")
async def execute_agent(request: GoalRequest):
    final, logs = await run_agent(request.goal)  # <- now async

    return {
        "status": "completed",
        "final": final,
    }
