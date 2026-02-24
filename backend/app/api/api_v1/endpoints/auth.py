from datetime import timedelta, datetime, timezone
import secrets
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from db.session import get_db
from db.models import User
from core import security
from core.config import settings
from schemas.token import Token
from services.email import send_forgot_password_email

router = APIRouter()

# In-memory token store: { token: { email, expires } }
# For production use a Redis/DB store instead
_reset_tokens: dict = {}


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/forgot-password", status_code=200)
async def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.
    Always returns 200 to prevent email enumeration.
    """
    result = await db.execute(select(User).filter(User.email == payload.email))
    user = result.scalars().first()
    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = {
            "email": payload.email,
            "expires": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        background_tasks.add_task(send_forgot_password_email, payload.email, token)
    return {"message": "If the email is registered, a reset link has been sent."}


@router.post("/reset-password", status_code=200)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using the token received by email."""
    token_data = _reset_tokens.get(payload.token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    if datetime.now(timezone.utc) > token_data["expires"]:
        _reset_tokens.pop(payload.token, None)
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    result = await db.execute(select(User).filter(User.email == token_data["email"]))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.hashed_password = security.get_password_hash(payload.new_password)
    await db.commit()
    _reset_tokens.pop(payload.token, None)
    return {"message": "Password reset successfully. You can now sign in."}
