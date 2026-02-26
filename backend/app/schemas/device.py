from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Shared properties
class DeviceBase(BaseModel):
    id: str
    name: Optional[str] = None
    type: Optional[str] = "esp32"

class DeviceCreate(DeviceBase):
    id: str # User must provide the unique ID (e.g. SH-001)
    name: str

class DeviceUpdate(DeviceBase):
    pass

class DeviceStateUpdate(BaseModel):
    # Flexible dict to allow arbitrary keys like "relay1", "relay2"
    # Or strict structure if preferred. Using dict for now to match current Firebase structure.
    state: Dict[str, Any]

class DeviceInDBBase(DeviceBase):
    id: str
    owner_id: int
    online: bool
    last_seen: Optional[datetime] = None
    ip_address: Optional[str] = None
    start_state: Optional[Dict[str, Any]] = {}
    api_key: Optional[str] = None

    class Config:
        from_attributes = True

class Device(DeviceInDBBase):
    pass
