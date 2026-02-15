import asyncio
from datetime import datetime
from sqlalchemy import select
from db.session import SessionLocal
from db.models import Schedule, Device
from api.api_v1.endpoints.devices import _update_relay_state

async def check_schedules():
    """
    Runs every minute to check for pending schedules.
    """
    print("⏰ Scheduler started...")
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # New DB session for this check
        async with SessionLocal() as db:
            # Find active schedules matching current time
            result = await db.execute(select(Schedule).filter(
                Schedule.is_active == True,
                Schedule.time == current_time
            ))
            schedules = result.scalars().all()
            
            for schedule in schedules:
                print(f"⚡ Executing Schedule: {schedule.time} -> Device {schedule.device_id}")
                try:
                    # Execute the action
                    # Note: We pass None for user because scheduler is a system action
                    await _update_relay_state(
                        db, 
                        schedule.device_id, 
                        schedule.relay_key, 
                        schedule.action, 
                        user_id=None # handled safely in updated _update_relay_state
                    )
                except Exception as e:
                    print(f"❌ Schedule Error: {e}")
                    
        # Sleep until next minute
        # Calculate seconds until next minute start to be precise
        now = datetime.now()
        sleep_seconds = 60 - now.second
        await asyncio.sleep(sleep_seconds)
