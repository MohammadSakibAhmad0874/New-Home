from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings

from api.api_v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def on_startup():
    # Not best practice for prod (use Alembic), but perfect for Phase 1 "quick start"
    print("🚀 Starting Application...")
    print(f"🔌 Connecting to DB: {settings.DATABASE_URL}")
    from db.session import engine, Base
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created.")
    except Exception as e:
        print(f"❌ DB Init Failed: {e}")

@app.get("/")
def root():
    return {"message": "Welcome to HomeControl BaaS", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
