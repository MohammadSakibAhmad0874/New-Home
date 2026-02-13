from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FirmwareBase(BaseModel):
    version: str
    description: Optional[str] = None

class FirmwareCreate(FirmwareBase):
    pass

class Firmware(FirmwareBase):
    id: int
    filename: str
    upload_date: datetime

    class Config:
        from_attributes = True
