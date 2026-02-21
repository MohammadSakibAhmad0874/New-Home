from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings

engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
SessionLocal = AsyncSessionLocal  # Alias for scheduler compatibility

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

