from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from db.session import get_db
from db.models import Device
from core.websocket import manager

router = APIRouter()

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for Devices and Frontend clients.
    """
    await manager.connect(websocket, device_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Parse message
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                # 1. Heartbeat from Device
                if msg_type == "heartbeat":
                     # Update last_seen in DB (optimize: maybe not every heartbeat to save DB writes)
                     # For now, let's just log it or update memory if we had an in-memory state.
                     # We can spawn a background task to update DB to avoid blocking WS loop.
                     pass 
                
                # 2. State Update from Device (Physical switch toggle)
                elif msg_type == "state_update":
                    new_state = message.get("data", {})
                    # Broadcast to all OTHER clients (Frontend)
                    await manager.broadcast(device_id, {"type": "update", "data": new_state})
                    
                    # Update DB (TODO: Optimize to not block)
                    # For Phase 2 Prototype, we can try to update DB here or just trust the device's next sync.
                    # Best practice: Update DB so REST API GET returns correct state.
                    result = await db.execute(select(Device).filter(Device.id == device_id))
                    device = result.scalars().first()
                    if device:
                        current_state = device.start_state or {}
                        current_state.update(new_state)
                        device.start_state = current_state
                        device.last_seen = datetime.utcnow()
                        device.online = True
                        db.add(device)
                        await db.commit()

                # 3. Command from Frontend (User toggled switch on UI)
                elif msg_type == "command":
                    # Broadcast to Device (and other frontends)
                    # {"type": "command", "data": {"relay1": {"state": true}}}
                    await manager.broadcast(device_id, message)
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, device_id)
        # Optional: Mark device offline if it was the device connection?
        # Hard to distinguish Device vs Frontend here without headers/auth.
