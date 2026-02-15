from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

# --- AI Service ---
class AIAnalysisRequest(BaseModel):
    user_id: int
    context: Optional[str] = None

class AIAnalysisResponse(BaseModel):
    user_id: int
    status: str
    confidence_score: float
    processing_time: str

# --- Email Service ---
class EmailRequest(BaseModel):
    email: EmailStr
    subject: Optional[str] = "Welcome"
    body: Optional[str] = None

class EmailResponse(BaseModel):
    sent: bool
    recipient: str

# --- Video Service ---
class VideoProcessRequest(BaseModel):
    camera_id: str
    duration: int = 10

class VideoProcessResponse(BaseModel):
    camera_id: str
    event: str
    frames: int
    timestamp: float

# --- Analytics Service ---
class AnalyticsRequest(BaseModel):
    period: str = "monthly"

class AnalyticsResponse(BaseModel):
    period: str
    total_users: int
    active_devices: int
    api_calls: int
