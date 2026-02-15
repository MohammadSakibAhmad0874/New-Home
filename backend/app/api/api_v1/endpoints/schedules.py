from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import Schedule, Device, User
from schemas.schedule import Schedule as ScheduleSchema, ScheduleCreate
from api import deps

router = APIRouter()

@router.get("/", response_model=List[ScheduleSchema])
async def read_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve schedules for current user.
    """
    # Join schedules with devices to filter by owner
    result = await db.execute(
        select(Schedule)
        .join(Device)
        .filter(Device.owner_id == current_user.id)
    )
    return result.scalars().all()

@router.post("/", response_model=ScheduleSchema)
async def create_schedule(
    *,
    db: AsyncSession = Depends(get_db),
    schedule_in: ScheduleCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new schedule.
    """
    # Verify device ownership
    result = await db.execute(select(Device).filter(Device.id == schedule_in.device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if device.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    schedule = Schedule(
        device_id=schedule_in.device_id,
        relay_key=schedule_in.relay_key,
        action=schedule_in.action,
        time=schedule_in.time
    )
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule

@router.delete("/{id}", response_model=ScheduleSchema)
async def delete_schedule(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a schedule.
    """
    result = await db.execute(select(Schedule).filter(Schedule.id == id))
    schedule = result.scalars().first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
        
    # Verify ownership via device
    device_result = await db.execute(select(Device).filter(Device.id == schedule.device_id))
    device = device_result.scalars().first()
    if device.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    await db.delete(schedule)
    await db.commit()
    return schedule
