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
        
    device = Device(
        id=device_in.id,
        name=device_in.name,
        type=device_in.type,
        owner_id=current_user.id,
        online=False
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
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
