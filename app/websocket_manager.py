# app/websocket_manager.py

from typing import List
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Send log message to all websocket clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

# instance used by agent & server
websocket_manager = WebSocketManager()
