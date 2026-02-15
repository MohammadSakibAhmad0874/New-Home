import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from db.session import engine
from sqlalchemy import text

async def inspect_db():
    print("🔌 Connecting to Database...")
    async with engine.begin() as conn:
        print("🔍 Checking 'devices' table columns...")
        result = await conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'devices'"))
        columns = result.fetchall()
        for col in columns:
            print(f" - {col[0]} ({col[1]})")

if __name__ == "__main__":
    asyncio.run(inspect_db())
