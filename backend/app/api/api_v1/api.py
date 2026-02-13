from fastapi import APIRouter
from api.api_v1.endpoints import auth, users, devices, websockets, integrations

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(websockets.router, tags=["websockets"])
api_router.include_router(integrations.router, prefix="/hooks", tags=["integrations"])
