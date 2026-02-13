from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Map device_id -> List of WebSockets (could be the device itself + multiple frontend clients)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
        self.active_connections[device_id].append(websocket)

    def disconnect(self, websocket: WebSocket, device_id: str):
        if device_id in self.active_connections:
            if websocket in self.active_connections[device_id]:
                self.active_connections[device_id].remove(websocket)
            if not self.active_connections[device_id]:
                del self.active_connections[device_id]

    async def broadcast(self, device_id: str, message: dict):
        if device_id in self.active_connections:
            # Send message to all connected clients for this device
            # Iterate over copy to avoid issues if connections drop during send
            for connection in self.active_connections[device_id][:]: 
                try:
                    await connection.send_json(message)
                except Exception:
                    # If send fails, assume disconnect and remove? 
                    # For now just log or ignore, disconnect usually handled by endpoint loop.
                    pass

manager = ConnectionManager()
