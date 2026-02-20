"""Database connection and session management."""
import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.database.models import Base  # noqa: F401 - ensure models are registered

# Prefer DATABASE_URL from env (Render, Docker, etc.); fallback to Settings (.env)
_database_url = os.getenv("DATABASE_URL") or get_settings().DATABASE_URL
if not _database_url:
    raise ValueError(
        "DATABASE_URL is not set. Set it in .env for local dev or in the environment for production (e.g. Render)."
    )

engine = create_engine(
    _database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
