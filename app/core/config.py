"""Application configuration loaded from environment variables."""
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env so os.getenv and BaseSettings see env vars (e.g. on Render, in shell)
load_dotenv()


class Settings(BaseSettings):
    """Application settings with validation."""

    # App
    APP_NAME: str = "Primetrade API"
    DEBUG: bool = False

    # Database – must be set via DATABASE_URL env (no hardcoded localhost for production)
    DATABASE_URL: str = ""

    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Redis (optional stub)
    REDIS_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
