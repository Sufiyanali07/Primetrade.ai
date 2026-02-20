"""Pytest fixtures: test client, db session, test user."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Use in-memory SQLite for tests if not overridden
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.database.models import Base, User, UserRole
from app.core.security import hash_password
from app.core.jwt_handler import create_access_token


# SQLite for tests (optional: use PostgreSQL via env)
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
if TEST_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create tables and yield a DB session. Teardown drops tables."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """Test client with overridden get_db."""
    from app.database.connection import get_db
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user (role=user)."""
    user = User(
        name="Test User",
        email="user@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user."""
    user = User(
        name="Admin User",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: User) -> str:
    """JWT for test user."""
    return create_access_token(subject=test_user.id, extra_claims={"role": test_user.role.value})


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """JWT for test admin."""
    return create_access_token(subject=test_admin.id, extra_claims={"role": test_admin.role.value})
