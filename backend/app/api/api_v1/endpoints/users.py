from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import User
from schemas.user import User as UserSchema, UserCreate
from api import deps
from core.security import get_password_hash
from services.email import send_welcome_email, send_admin_promotion_email

router = APIRouter()

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create new user and send welcome confirmation email.
    """
    result = await db.execute(select(User).filter(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Send welcome email in background (non-blocking)
    background_tasks.add_task(send_welcome_email, user.email)

    return user


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.delete("/{user_id}", response_model=UserSchema)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete own user")
        
    await db.delete(user)
    await db.commit()
    return user


@router.put("/{user_id}/promote", response_model=UserSchema)
async def promote_user(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    [ADMIN] Promote a user to superuser and send them an email notification.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_superuser:
        raise HTTPException(status_code=400, detail="User is already a superuser")

    user.is_superuser = True
    user.is_active    = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Notify the newly promoted admin by email (non-blocking)
    background_tasks.add_task(send_admin_promotion_email, user.email)

    return user

