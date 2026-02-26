import asyncio
from datetime import datetime, timedelta
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
                        schedule.action
                        # current_user=None by default — system action, no user auth needed
                    )
                except Exception as e:
                    print(f"❌ Schedule Error: {e}")
                    
        # Sleep until next minute
        # Calculate seconds until next minute start to be precise
        now = datetime.now()
        sleep_seconds = 60 - now.second
        await asyncio.sleep(sleep_seconds)


async def check_device_online_status():
    """
    Runs every 60 seconds.
    Marks any device as offline if it hasn't sent a heartbeat in the last 5 minutes.
    This prevents devices from staying 'online' forever after they disconnect.
    """
    print("📡 Device online-status watcher started...")
    OFFLINE_THRESHOLD = timedelta(minutes=5)
    while True:
        try:
            async with SessionLocal() as db:
                cutoff = datetime.utcnow() - OFFLINE_THRESHOLD
                result = await db.execute(
                    select(Device).filter(
                        Device.online == True,
                        Device.last_seen < cutoff
                    )
                )
                stale_devices = result.scalars().all()
                for device in stale_devices:
                    device.online = False
                    db.add(device)
                    print(f"📴 Device {device.id} marked offline (last seen: {device.last_seen})")
                if stale_devices:
                    await db.commit()
        except Exception as e:
            print(f"❌ Online-status watcher error: {e}")

        await asyncio.sleep(60)

