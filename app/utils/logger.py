"""Centralized logging configuration."""
import logging
import sys
from typing import Any

from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG if get_settings().DEBUG else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger


def log_request(method: str, path: str, status_code: int, **extra: Any) -> None:
    """Log HTTP request (for middleware)."""
    logger = get_logger("http")
    logger.info(
        "%s %s %s",
        method,
        path,
        status_code,
        extra=extra,
    )
