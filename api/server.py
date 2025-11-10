# api/server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agentic_planner import run_agent
from app.websocket_manager import websocket_manager


# --------------------------------------------------------
# ✅ FastAPI App + CORS Fix (important for Render deploy)
# --------------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow Streamlit + localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------
# ✅ REST API
# --------------------------------------------------------
class GoalRequest(BaseModel):
    goal: str


@app.post("/run-agent")
async def execute_agent(request: GoalRequest):
    """Runs the Multi-Agent Planner and returns result."""
    final, logs = await run_agent(request.goal)
    return {"status": "completed", "final": final, "logs": logs}


@app.get("/status")
async def status():
    """UI checks this to detect GPT mode (online/offline)."""
    from app.agentic_planner import api_key
    return {"mode": "online" if api_key else "offline"}


# --------------------------------------------------------
# ✅ WebSocket for Streaming Logs (Devin style timeline)
# --------------------------------------------------------
@app.websocket("/ws/")        # <-- IMPORTANT trailing slash
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # We don't care what UI sends
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
