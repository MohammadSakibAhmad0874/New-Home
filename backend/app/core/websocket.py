from typing import Dict, List
from fastapi import WebSocket
import httpx
from core.config import settings

class ConnectionManager:
    def __init__(self):
        # Map device_id -> List of WebSockets (could be the device itself + multiple frontend clients)
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
            # First connection for this device ID = Device Online (likely)
            await self.send_notification(f"Device {device_id} is Online 🟢")
            
        self.active_connections[device_id].append(websocket)

    def disconnect(self, websocket: WebSocket, device_id: str):
        if device_id in self.active_connections:
            if websocket in self.active_connections[device_id]:
                self.active_connections[device_id].remove(websocket)
            
            if not self.active_connections[device_id]:
                del self.active_connections[device_id]
                # Last connection gone = Device Offline (likely)
                # Note: This is a synchronous method, so we can't await. 
                # Ideally, we should use background tasks or make disconnect async.
                # However, FastAPI's disconnect is often called in exception handlers.
                # Hack: Use httpx.post (sync) or schedule async task. 
                # Since we are in an async loop context (usually), we can't easily block.
                # Let's try to just print for now or use a fire-and-forget approach if possible, 
                # OR better: change disconnect signature if usage allows, but it's called from catch block.
                # Actually, we can use a non-blocking way or just ignore for now to avoid freezing.
                # Let's use a sync call with short timeout for simplicity in this prototype.
                try:
                    httpx.post(f"https://ntfy.sh/{settings.NTFY_TOPIC}", 
                        data=f"Device {device_id} is Offline 🔴",
                        headers={"Title": "HomeControl Alert", "Priority": "high"},
                        timeout=2.0
                    )
                except:
                    pass

    async def send_notification(self, message: str):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"https://ntfy.sh/{settings.NTFY_TOPIC}", 
                    data=message,
                    headers={"Title": "HomeControl Alert"}
                )
        except Exception as e:
            print(f"Failed to send notification: {e}")

    async def broadcast(self, device_id: str, message: dict):
        if device_id in self.active_connections:
            # Send message to all connected clients for this device
            for connection in self.active_connections[device_id][:]: 
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()
