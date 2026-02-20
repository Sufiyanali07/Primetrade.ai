"""User service: get user by id, list users (admin)."""
from app.database.models import User
from app.database.schemas import UserResponse
from app.utils.exceptions import NotFoundException
from sqlalchemy.orm import Session


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID or raise 404."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundException("User not found")
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserResponse]:
    """List users with pagination."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]
