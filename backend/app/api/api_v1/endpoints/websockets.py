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
    print(f"🔌 WS connect attempt → device_id={device_id} | api_key={'SET' if api_key else 'NONE'} | token={'SET' if token else 'NONE'}")

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
        if not device:
            print(f"❌ WS REJECTED: No device found with api_key={api_key[:10]}... (device not registered in DB?)")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        if device.id != device_id:
            print(f"❌ WS REJECTED: api_key belongs to device '{device.id}' but requested device_id='{device_id}'")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        is_device = True
        print(f"✅ WS AUTH OK: Device '{device_id}' authenticated via api_key")
        
    elif token:
        # Validate User Token
        try:
            from jose import jwt
            from core.config import settings
            
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            print(f"✅ WS AUTH OK: User authenticated via token for device_id={device_id}")
        except Exception as e:
            print(f"❌ WS REJECTED: Invalid token for device_id={device_id} → {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    else:
        print(f"❌ WS REJECTED: No api_key or token provided for device_id={device_id}")
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
                
                # 1. Heartbeat from Device — update DB to keep device marked as online
                if msg_type == "heartbeat":
                    try:
                        result = await db.execute(select(Device).filter(Device.id == device_id))
                        dev = result.scalars().first()
                        if dev:
                            dev.last_seen = datetime.utcnow()
                            dev.online = True
                            db.add(dev)
                            await db.commit()
                    except Exception:
                        pass  # Non-fatal — don't kill the WS connection over a heartbeat update failure
                
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
