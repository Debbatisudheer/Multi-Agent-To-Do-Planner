# api/server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.agentic_planner import run_agent
from app.websocket_manager import websocket_manager

app = FastAPI()

# ✅ IMPORTANT: allow Streamlit + Render frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # ← allow all (easier for now)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():
    return {"mode": "online"}

@app.post("/run-agent")
async def execute_agent(request: dict):
    final = await run_agent(request["goal"])
    return {"final": final}

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
