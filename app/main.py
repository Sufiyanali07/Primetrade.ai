"""FastAPI application entry point with CORS, exception handling, logging."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.database.connection import engine
from app.database.models import Base
from app.utils.exceptions import AppException
from app.utils.logger import get_logger, log_request

from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_users import router as users_router
from app.api.v1.routes_products import router as products_router

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup (optional; Alembic preferred in production)."""
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log every request and response status."""
    response = await call_next(request)
    log_request(request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    """Centralized handler for AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Input sanitization / validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# API v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}
