"""Users API: list users (admin)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import require_admin
from app.database.connection import get_db
from app.database.models import User
from app.database.schemas import UserResponse
from app.services.user_service import list_users
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users_route(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all users (admin only)."""
    return list_users(db, skip=skip, limit=limit)
