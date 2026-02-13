import asyncio
from db.session import engine, Base
from db.models import User, Device # Ensure models are imported

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Uncomment to reset DB
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized")

if __name__ == "__main__":
    asyncio.run(init_db())
