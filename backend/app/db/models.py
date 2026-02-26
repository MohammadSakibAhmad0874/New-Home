from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, JSON, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.session import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    devices = relationship("Device", back_populates="owner")

class Device(Base):
    __tablename__ = "devices"

    id = Column(String, primary_key=True, index=True) # "SH-001"
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    type = Column(String, default="esp32")
    api_key = Column(String, unique=True, index=True) # Nullable removed
    
    online = Column(Boolean, default=False)
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    ip_address = Column(String, nullable=True)
    
    # Store relay state as JSON: {"relay1": {"state": true}, ...}
    start_state = Column(JSON, default={})
    
    owner = relationship("User", back_populates="devices")


class Firmware(Base):
    __tablename__ = "firmware"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True, nullable=False) # e.g. "1.0.1"
    filename = Column(String)
    description = Column(String, nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Store binary data directly in DB for simplicity
    data = Column(LargeBinary)

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.id"), index=True)
    relay_key = Column(String, nullable=False)
    action = Column(Boolean, default=True)
    time = Column(String, nullable=False)  # HH:MM format
    is_active = Column(Boolean, default=True)

    device = relationship("Device")

