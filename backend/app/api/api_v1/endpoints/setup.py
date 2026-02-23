"""
One-time admin setup endpoint.
Call GET /api/v1/setup/create-admin once to create or reset the admin account.
This endpoint is protected by a secret token.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import User
from core.security import get_password_hash

router = APIRouter()

# ─── CHANGE THIS SECRET if you want more security ───
SETUP_SECRET = "homecontrol_setup_2024"

ADMIN_EMAIL    = "ahmadsakib263@gmail.com"
ADMIN_PASSWORD = "MrNoor@874"

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
        # Update existing user
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
        # Create new admin user
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
