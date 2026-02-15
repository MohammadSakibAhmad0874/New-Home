from typing import Optional
from pydantic import BaseModel

class ScheduleBase(BaseModel):
    device_id: str
    relay_key: str
    action: bool
    time: str  # HH:MM

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
