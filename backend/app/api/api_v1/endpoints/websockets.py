from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from db.session import get_db
from db.models import Device
from core.websocket import manager
from api import deps

router = APIRouter()

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Query(None),
    api_key: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for Devices and Frontend clients.
    Secure: Requires either 'token' (User) or 'api_key' (Device).
    Device can also use 'Authorization' header.
    """
    # 1. Authenticate
    is_device = False
    
    # Check headers for Device Auth (standard for some clients)
    auth_header = websocket.headers.get("Authorization")
    if auth_header and not api_key:
        try:
            scheme, key = auth_header.split()
            if scheme.lower() == "bearer":
                api_key = key
        except:
            pass
            
    if api_key:
        # Validate Device Key
        result = await db.execute(select(Device).filter(Device.api_key == api_key))
        device = result.scalars().first()
        if not device or device.id != device_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        is_device = True
        
    elif token:
        # Validate User Token
        try:
            # We can reuse the dependency logic manually
            # But get_current_user is async and takes Depends... 
            # Easier to just replicate the decode logic or call a helper
            from jose import jwt
            from core.config import settings
            
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            # Valid token
        except Exception:
             await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
             return
    else:
        # No auth
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

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

                # 3. Sensor Update from Device (Temperature/Humidity)
                elif msg_type == "sensor_update":
                    sensor_data = message.get("data", {})
                    # Broadcast to Frontend
                    await manager.broadcast(device_id, {"type": "sensor_update", "data": sensor_data})
                    
                    # Update DB
                    try:
                        result = await db.execute(select(Device).filter(Device.id == device_id))
                        device = result.scalars().first()
                        if device:
                            if "temperature" in sensor_data:
                                device.temperature = float(sensor_data["temperature"])
                            if "humidity" in sensor_data:
                                device.humidity = float(sensor_data["humidity"])
                            device.last_seen = datetime.now() # Use naive datetime or aware based on config
                            # device.last_seen = datetime.utcnow() # Deprecated in Python 3.12+
                            # Using server_default func.now() usually handles it
                            db.add(device)
                            await db.commit()
                    except Exception as e:
                        print(f"Error updating sensor data: {e}")

                # 4. Command from Frontend (User toggled switch on UI)
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
