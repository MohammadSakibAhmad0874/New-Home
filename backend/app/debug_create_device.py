import asyncio
import sys
import os
import secrets

sys.path.append(os.path.dirname(__file__)) # Add app/ directory

from db.session import engine, AsyncSession
from db.models import Device, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

async def debug_creation():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as db:
        print("🔍 checking user...")
        # Get user
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        if not user:
            print("❌ No users found!")
            return
        
        print(f"👤 Found User: {user.email} (ID: {user.id})")
        
        api_key = secrets.token_urlsafe(32)
        device_id = f"DEBUG-{secrets.token_hex(4)}"
        
        device = Device(
            id=device_id,
            name="Debug Device",
            type="esp32",
            owner_id=user.id,
            online=False,
            api_key=api_key
        )
        
        print(f" Attempting to create Device: {device_id}")
        try:
            db.add(device)
            await db.commit()
            print("✅ Device created successfully!")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Ensure DATABASE_URL is set
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/homecontrol"
        
    asyncio.run(debug_creation())
