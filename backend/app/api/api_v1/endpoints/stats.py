from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api import deps
from db import models
# We need a schema for reading, let's define a simple one here or import if exists
from pydantic import BaseModel

router = APIRouter()

class SensorDataPoint(BaseModel):
    timestamp: datetime
    temperature: float | None
    humidity: float | None

    class Config:
        from_attributes = True

@router.get("/{device_id}/stats", response_model=List[SensorDataPoint])
def get_device_stats(
    device_id: str,
    hours: int = 24,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get historical sensor data for a device.
    """
    # Verify device exists and user has access (for now assuming owner or admin)
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Simple permission check
    if not current_user.is_superuser and device.owner_id != current_user.id:
         raise HTTPException(status_code=400, detail="Not enough permissions")

    since = datetime.utcnow() - timedelta(hours=hours)
    
    readings = db.query(models.SensorReading).filter(
        models.SensorReading.device_id == device_id,
        models.SensorReading.timestamp >= since
    ).order_by(models.SensorReading.timestamp.asc()).all()
    
    return readings
