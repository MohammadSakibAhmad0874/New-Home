import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../")) # Add app/ directory

from db.session import engine
from sqlalchemy import text

async def update_db():
    print("🔌 Connecting to Database...")
    async with engine.begin() as conn:
        print("🛠 Adding 'api_key' column to 'devices' table...")
        try:
            # Check if column exists (naive verify or just try add)
            # PostgreSQL allows ADD COLUMN IF NOT EXISTS in newer versions, 
            # but standard SQL is ALTER TABLE.
            # simpler to catch error or just run it. 
            await conn.execute(text("ALTER TABLE devices ADD COLUMN IF NOT EXISTS api_key VARCHAR"))
            await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_devices_api_key ON devices (api_key)"))
            print("✅ Column 'api_key' added successfully.")
        except Exception as e:
            print(f"⚠️ Error (might already exist): {e}")

if __name__ == "__main__":
    asyncio.run(update_db())
