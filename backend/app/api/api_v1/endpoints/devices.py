from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from db.session import get_db
from db.models import Device, User
from schemas.device import Device as DeviceSchema, DeviceCreate, DeviceStateUpdate
from api import deps

router = APIRouter()

@router.get("/admin/all", response_model=List[DeviceSchema])
async def read_all_devices_admin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
    skip: int = 0,
    limit: int = 500,
) -> Any:
    """
    [ADMIN] Retrieve ALL devices from all users.
    """
    result = await db.execute(
        select(Device).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.delete("/admin/{device_id}")
async def admin_delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    [ADMIN] Delete any device by ID.
    """
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await db.delete(device)
    await db.commit()
    return {"status": "deleted", "device_id": device_id}

@router.put("/admin/{device_id}/rename")
async def admin_rename_device(
    device_id: str,
    name: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    [ADMIN] Rename any device.
    """
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.name = name
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device

@router.get("/", response_model=List[DeviceSchema])
async def read_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve devices owned by current user.
    """
    result = await db.execute(
        select(Device).filter(Device.owner_id == current_user.id).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=DeviceSchema)
async def create_device(
    *,
    db: AsyncSession = Depends(get_db),
    device_in: DeviceCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Register a new device.
    """
    result = await db.execute(select(Device).filter(Device.id == device_in.id))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Device with this ID already exists")
        
    import secrets
    api_key = secrets.token_urlsafe(32)
    
    device = Device(
        id=device_in.id,
        name=device_in.name,
        type=device_in.type,
        owner_id=current_user.id,
        online=False,
        api_key=api_key
    )
    try:
        db.add(device)
        await db.commit()
        await db.refresh(device)
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    return device

@router.get("/{device_id}", response_model=DeviceSchema)
async def read_device(
    *,
    db: AsyncSession = Depends(get_db),
    device_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get device by ID.
    """
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return device

from core.websocket import manager

@router.put("/{device_id}/state")
async def update_device_state(
    *,
    db: AsyncSession = Depends(get_db),
    device_id: str,
    state_update: Dict[str, Any] = Body(...),
) -> Any:
    """
    Update device state (relays).
    """
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Update state
    current_state = device.start_state or {}
    current_state.update(state_update)
    
    device.start_state = current_state
    device.last_seen = datetime.utcnow()
    
    db.add(device)
    await db.commit()
    
    # Notify WebSocket clients
    await manager.broadcast(device_id, {"type": "update", "data": device.start_state})
    
    return {"status": "success", "state": device.start_state}

@router.post("/{device_id}/heartbeat")
async def heartbeat(
    *,
    db: AsyncSession = Depends(get_db),
    device_id: str,
    ip: str = Body(..., embed=True),
) -> Any:
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device.last_seen = datetime.utcnow()
    device.online = True
    device.ip_address = ip
    
    db.add(device)
    await db.commit()
    return {"status": "online"}

@router.post("/{device_id}/relays/{relay_key}/on")
async def turn_relay_on(
    device_id: str,
    relay_key: str,
    api_key: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Turn a specific relay ON.
    """
    return await _update_relay_state(db, device_id, relay_key, True, current_user, api_key)

@router.post("/{device_id}/relays/{relay_key}/off")
async def turn_relay_off(
    device_id: str,
    relay_key: str,
    api_key: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Turn a specific relay OFF.
    """
    return await _update_relay_state(db, device_id, relay_key, False, current_user, api_key)

async def _update_relay_state(db: AsyncSession, device_id: str, relay_key: str, state: bool, current_user: User = None, api_key: str = None):
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Auth Logic: API Key OR User
    authorized = False
    
    # 1. Check API Key (Device Level)
    if api_key and device.api_key == api_key:
        authorized = True
        
    # 2. Check User (Owner)
    if not authorized and current_user:
        if device.owner_id == current_user.id or current_user.is_superuser:
            authorized = True
            
    if not authorized:
        raise HTTPException(status_code=401, detail="Not authorized (Invalid API Key or Token)")

    current_state = device.start_state or {}
    
    # Update specific relay
    if relay_key not in current_state:
        current_state[relay_key] = {}
    
    current_state[relay_key]["state"] = state
    
    device.start_state = current_state
    device.last_seen = datetime.utcnow()
    
    db.add(device)
    await db.commit()
    
    # Notify WebSocket clients
    await manager.broadcast(device_id, {"type": "update", "data": {relay_key: {"state": state}}})
    
    return {"status": "success", "state": device.start_state}
