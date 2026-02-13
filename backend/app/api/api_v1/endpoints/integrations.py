from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from core.config import settings
from api.api_v1.endpoints.websockets import manager
from db.models import Device
from pydantic import BaseModel
from sqlalchemy.future import select

router = APIRouter()

class VoiceCommand(BaseModel):
    device_id: str
    relay: int # 1-based index (1, 2, 3, 4)
    state: bool

@router.post("/control", status_code=status.HTTP_200_OK)
async def voice_control(
    command: VoiceCommand,
    x_webhook_secret: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Control device via Webhook (IFTTT, Siri, etc).
    Requires 'X-Webhook-Secret' header matching config.
    """
    if x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Webhook Secret")

    # 1. Get Device
    result = await db.execute(select(Device).where(Device.id == command.device_id))
    device = result.scalars().first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # 2. Update State
    if device.start_state is None:
        device.start_state = {}
    
    relay_key = f"relay{command.relay}"
    
    # Update DB state
    if relay_key not in device.start_state:
        device.start_state[relay_key] = {}
        
    device.start_state[relay_key]["state"] = command.state
    
    # Mark as modified for SQLAlchemy to detect JSON change
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(device, "start_state")
    
    await db.commit()
    await db.refresh(device)

    # 3. Broadcast to WebSocket
    await manager.broadcast_to_device(
        command.device_id,
        {relay_key: {"state": command.state}}
    )

    return {"status": "success", "device": command.device_id, "relay": command.relay, "new_state": command.state}
