import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from db.session import engine
from sqlalchemy import text

async def add_sensor_columns():
    print("🔌 Connecting to Database...")
    async with engine.begin() as conn:
        print("🛠️ Adding 'temperature' and 'humidity' columns to 'devices' table...")
        
        # Add temperature
        try:
            await conn.execute(text("ALTER TABLE devices ADD COLUMN temperature FLOAT"))
            print("✅ Column 'temperature' added.")
        except Exception as e:
            if "already exists" in str(e):
                 print("⚠️ Column 'temperature' already exists.")
            else:
                 print(f"❌ Error adding 'temperature': {e}")

        # Add humidity
        try:
            await conn.execute(text("ALTER TABLE devices ADD COLUMN humidity FLOAT"))
            print("✅ Column 'humidity' added.")
        except Exception as e:
            if "already exists" in str(e):
                 print("⚠️ Column 'humidity' already exists.")
            else:
                 print(f"❌ Error adding 'humidity': {e}")
                 
        print("🔄 Verification complete.")

if __name__ == "__main__":
    # Ensure DATABASE_URL is set
    if not os.environ.get("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/homecontrol"
        
    asyncio.run(add_sensor_columns())
