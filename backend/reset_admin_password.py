"""
Run this once to reset the admin password in the Render database.
Usage: python reset_admin_password.py
"""
import asyncio, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from db.session import engine
from db.models import User
from core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ADMIN_EMAIL   = "ahmadsakib263@gmail.com"
NEW_PASSWORD  = "MrNoor@874"

async def reset():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        user = result.scalars().first()
        if not user:
            print(f"❌ User '{ADMIN_EMAIL}' not found!")
            return
        user.hashed_password = get_password_hash(NEW_PASSWORD)
        user.is_superuser    = True
        user.is_active       = True
        session.add(user)
        await session.commit()
        print(f"✅ Password reset for {ADMIN_EMAIL}")
        print(f"✅ is_superuser = True")
        print(f"   You can now login at /admin.html")

asyncio.run(reset())
