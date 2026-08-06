"""
Dependency utilities for the FastAPI application.
Provides database session management for endpoint handlers, ensuring
proper opening and closing of sessions per HTTP request lifecycle.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator that yields a SQLAlchemy database session.
    Ensures that the database connection is safely closed after the request is processed.

    Yields:
        Generator[Session, None, None]: An active SQLAlchemy database session context.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
