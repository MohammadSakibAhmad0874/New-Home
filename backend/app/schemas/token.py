from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None  # seconds until expiry

class TokenPayload(BaseModel):
    sub: Optional[str] = None
