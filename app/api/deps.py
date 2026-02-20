"""FastAPI dependencies: current user, admin check."""
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.jwt_handler import decode_access_token
from app.database.connection import get_db
from app.database.models import User, UserRole
from app.services.user_service import get_user_by_id
from app.utils.exceptions import UnauthorizedException, ForbiddenException


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate JWT, return current user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException("Invalid or expired token")
    user_id = int(payload["sub"])
    return get_user_by_id(db, user_id)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require current user to have admin role."""
    if current_user.role != UserRole.admin:
        raise ForbiddenException("Admin access required")
    return current_user
