"""Authentication service: registration, login, token creation."""
from app.core.jwt_handler import create_access_token
from app.core.security import hash_password, verify_password
from app.database.models import User, UserRole
from app.database.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.utils.exceptions import UnauthorizedException, ConflictException
from sqlalchemy.orm import Session


def register_user(db: Session, data: UserCreate) -> UserResponse:
    """Register a new user. Email must be unique."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ConflictException("Email already registered")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.user,  # public registration always gets 'user' role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def login_user(db: Session, data: LoginRequest) -> TokenResponse:
    """Authenticate user and return JWT."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password")
    token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.role.value, "email": user.email},
    )
    return TokenResponse(access_token=token)
