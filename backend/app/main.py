from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# ─── Standardised Error Handlers ─────────────────────────────────────────────

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"status": 404, "detail": "Not found"})

@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    return JSONResponse(status_code=500, content={"status": 500, "detail": "Internal server error"})

# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    # Not best practice for prod (use Alembic), but perfect for Phase 1 "quick start"
    print("🚀 Starting Application...")
    print(f"🔌 Connecting to DB: {settings.DATABASE_URL}")
    from db.session import engine, Base
    from sqlalchemy import text
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created.")
    except Exception as e:
        err = str(e)
        if "getaddrinfo" in err or "could not translate" in err:
            print(f"❌ DB Init Failed: Cannot reach database host.")
            print(f"   ➡️  Is DATABASE_URL set correctly in backend/.env?")
            print(f"   ➡️  For local dev: copy External URL from Render → homecontrol-db → Connect")
        else:
            print(f"❌ DB Init Failed: {e}")

    # ── Safe column migrations (ADD/DROP IF EXISTS) ─────────────────────────
    # These are idempotent — safe to run on every startup.
    migrations = [
        # Add new columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR;",
        # Drop stale sensor columns removed in temperature-sensor cleanup
        "ALTER TABLE devices DROP COLUMN IF EXISTS temperature;",
        "ALTER TABLE devices DROP COLUMN IF EXISTS humidity;",
    ]
    try:
        async with engine.begin() as conn:
            for sql in migrations:
                await conn.execute(text(sql))
                print(f"✅ Migration OK: {sql.strip()}")
    except Exception as e:
        print(f"⚠️  Migration warning (non-fatal): {e}")
        
    # Start Schedulers
    import asyncio
    from core.scheduler import check_schedules, check_device_online_status, keep_alive_ping
    asyncio.create_task(check_schedules())
    asyncio.create_task(check_device_online_status())
    asyncio.create_task(keep_alive_ping())
    print("✅ Background schedulers started.")

# ─── Health Endpoints ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Welcome to HomeControl BaaS", "docs": "/docs"}

@app.get("/health")
async def health_check():
    """Basic health check with DB connectivity probe."""
    db_status = "unknown"
    try:
        from db.session import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "database": db_status}

@app.get(settings.API_V1_STR + "/health")
async def health_check_v1():
    """Versioned health check with DB connectivity probe."""
    db_status = "unknown"
    try:
        from db.session import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "database": db_status}

