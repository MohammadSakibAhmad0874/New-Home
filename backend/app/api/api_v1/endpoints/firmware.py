from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.session import get_db
from db.models import Firmware as FirmwareModel
from schemas.firmware import Firmware as FirmwareSchema
from api import deps

router = APIRouter()

@router.post("/upload", response_model=FirmwareSchema)
async def upload_firmware(
    version: str,
    description: str = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Upload new firmware version (Admin only).
    """
    # Check if version exists
    result = await db.execute(select(FirmwareModel).filter(FirmwareModel.version == version))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Version already exists")

    content = await file.read()
    
    firmware = FirmwareModel(
        version=version,
        description=description,
        filename=file.filename,
        data=content
    )
    db.add(firmware)
    await db.commit()
    await db.refresh(firmware)
    return firmware

@router.get("/check")
async def check_update(
    current_version: str = None, # ESP32 sends its current version
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Check for latest firmware.
    Returns JSON with latest version and download URL.
    """
    # Get latest version (order by id desc or upload_date desc)
    # Using ID for simplicity as newer uploads = higher ID usually
    result = await db.execute(select(FirmwareModel).order_by(desc(FirmwareModel.id)))
    latest = result.scalars().first()
    
    if not latest:
        return {"message": "No firmware available"}
        
    return {
        "version": latest.version,
        "url": f"/api/v1/firmware/download/{latest.version}",
        "description": latest.description
    }

@router.get("/download/{version}")
async def download_firmware(
    version: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download firmware binary.
    """
    result = await db.execute(select(FirmwareModel).filter(FirmwareModel.version == version))
    firmware = result.scalars().first()
    
    if not firmware:
        raise HTTPException(status_code=404, detail="Firmware not found")
        
    # Return binary as octet-stream
    return Response(
        content=firmware.data,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={firmware.filename}"}
    )

@router.get("/", response_model=List[FirmwareSchema])
async def list_firmware(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    current_user: Any = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    List all firmware versions.
    """
    result = await db.execute(select(FirmwareModel).order_by(desc(FirmwareModel.id)).offset(skip).limit(limit))
    return result.scalars().all()
