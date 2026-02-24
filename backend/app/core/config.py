from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "HomeControl BaaS"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db/homecontrol"
    
    # Redis (optional — not needed for free deployment)
    REDIS_URL: str = ""
    
    # RabbitMQ (optional — not needed for free deployment)
    RABBITMQ_URL: str = ""
    
    # Security
    SECRET_KEY: str = "supersecretkey_change_me_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Integrations
    WEBHOOK_SECRET: str = "voice_secret_123"
    NTFY_TOPIC: str = "homecontrol_ghosty_alerts"

    # Email (Resend.com — sign up free at resend.com, set this in Render env vars)
    RESEND_API_KEY: str = ""    # e.g. re_xxxxxxxxxxxxxxxx

    
    class Config:
        case_sensitive = True

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

settings = Settings()
