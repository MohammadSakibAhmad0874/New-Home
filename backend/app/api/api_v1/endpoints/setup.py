"""
One-time admin setup endpoint.
Call GET /api/v1/setup/create-admin once to create or reset the admin account.
This endpoint is protected by a secret token.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from db.session import get_db
from db.models import User
from core.security import get_password_hash

router = APIRouter()

# ─── CHANGE THIS SECRET if you want more security ───
SETUP_SECRET = "homecontrol_setup_2024"

ADMIN_EMAIL    = "admin@homecontrol.com"
ADMIN_PASSWORD = "Admin123@"

@router.get("/create-admin")
async def create_admin(secret: str, db: AsyncSession = Depends(get_db)):
    """
    One-time endpoint to create or reset the admin user.
    Call: GET /api/v1/setup/create-admin?secret=homecontrol_setup_2024
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
    user = result.scalars().first()

    hashed = get_password_hash(ADMIN_PASSWORD)

    if user:
        user.hashed_password = hashed
        user.is_superuser    = True
        user.is_active       = True
        db.add(user)
        await db.commit()
        return {
            "status": "updated",
            "email": ADMIN_EMAIL,
            "is_superuser": True,
            "message": "Admin password reset. You can now login at /admin.html"
        }
    else:
        new_user = User(
            email=ADMIN_EMAIL,
            hashed_password=hashed,
            is_active=True,
            is_superuser=True,
        )
        db.add(new_user)
        await db.commit()
        return {
            "status": "created",
            "email": ADMIN_EMAIL,
            "is_superuser": True,
            "message": "Admin created. You can now login at /admin.html"
        }


@router.get("/delete-users")
async def delete_users(secret: str, ids: str, db: AsyncSession = Depends(get_db)):
    """
    One-time endpoint to delete users by ID.
    Call: GET /api/v1/setup/delete-users?secret=homecontrol_setup_2024&ids=1,5
    ids = comma-separated user IDs to delete.
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    try:
        id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ids format. Use: ids=1,5")

    if not id_list:
        raise HTTPException(status_code=400, detail="No valid IDs provided")

    deleted = []
    for uid in id_list:
        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalars().first()
        if user:
            deleted.append({"id": user.id, "email": user.email})
            await db.delete(user)

    await db.commit()
    return {
        "status": "done",
        "deleted": deleted,
        "count": len(deleted),
        "message": f"Deleted {len(deleted)} user(s). You can remove this endpoint now."
    }


@router.get("/device-key")
async def get_device_key(secret: str, device_id: str, db: AsyncSession = Depends(get_db)):
    """
    Lookup API key for a device.
    Call: GET /api/v1/setup/device-key?secret=homecontrol_setup_2024&device_id=SH-004
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    from db.models import Device
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    return {
        "device_id": device.id,
        "api_key": device.api_key,
        "name": device.name,
        "owner_id": device.owner_id
    }


@router.get("/create-device")
async def create_device(
    secret: str,
    device_id: str,
    owner_id: int,
    name: str = "New Device",
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new device.
    Call: GET /api/v1/setup/create-device?secret=homecontrol_setup_2024&device_id=SH-001&owner_id=2&name=My+Device
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    from db.models import Device
    import secrets as sec

    # Check if already exists
    result = await db.execute(select(Device).where(Device.id == device_id))
    existing = result.scalars().first()
    if existing:
        return {
            "status": "already_exists",
            "device_id": existing.id,
            "api_key": existing.api_key,
            "name": existing.name,
            "owner_id": existing.owner_id,
            "message": "Device already registered. Use the api_key shown above."
        }

    api_key = sec.token_urlsafe(32)
    device = Device(
        id=device_id,
        owner_id=owner_id,
        name=name,
        type="esp32",
        api_key=api_key,
        online=False,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return {
        "status": "created",
        "device_id": device.id,
        "api_key": device.api_key,
        "name": device.name,
        "owner_id": device.owner_id,
        "message": "Device registered! Copy the api_key into your config.h"
    }


@router.get("/force-register-device")
async def force_register_device(
    secret: str,
    device_id: str,
    owner_id: int,
    api_key: str,
    name: str = "ESP32 Device",
    db: AsyncSession = Depends(get_db),
):
    """
    Force-register a device with an EXACT api_key (for firmware-hardcoded keys).
    If device already exists, updates the api_key.
    Call: GET /api/v1/setup/force-register-device?secret=homecontrol_setup_2024
               &device_id=SH-004&owner_id=1&api_key=YOUR_KEY&name=SH-004+Device
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    from db.models import Device

    result = await db.execute(select(Device).where(Device.id == device_id))
    existing = result.scalars().first()
    if existing:
        # Update the api_key to match what firmware has
        old_key = existing.api_key
        existing.api_key = api_key
        existing.name = name
        db.add(existing)
        await db.commit()
        return {
            "status": "updated",
            "device_id": existing.id,
            "api_key": api_key,
            "old_api_key": old_key,
            "message": "Device api_key updated to match firmware. Reconnect ESP32 now."
        }

    device = Device(
        id=device_id,
        owner_id=owner_id,
        name=name,
        type="esp32",
        api_key=api_key,
        online=False,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return {
        "status": "created",
        "device_id": device.id,
        "api_key": device.api_key,
        "name": device.name,
        "owner_id": device.owner_id,
        "message": "Device registered with exact firmware api_key!"
    }


@router.get("/list-devices")
async def list_devices(secret: str, db: AsyncSession = Depends(get_db)):
    """
    List all registered devices and their api_keys.
    Call: GET /api/v1/setup/list-devices?secret=homecontrol_setup_2024
    """
    if secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    from db.models import Device
    result = await db.execute(select(Device))
    devices = result.scalars().all()
    return {
        "count": len(devices),
        "devices": [
            {
                "id": d.id,
                "name": d.name,
                "owner_id": d.owner_id,
                "api_key": d.api_key,
                "online": d.online,
                "last_seen": str(d.last_seen),
            }
            for d in devices
        ]
    }
