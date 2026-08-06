"""
Database configuration and setup module.
Configures the SQLite database connection engine, session factory, 
and base class for SQLAlchemy ORM models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database connection URL (SQLite local database)
DATABASE_URL = "sqlite:///taab.db"

# Create the SQLAlchemy database engine
# check_same_thread is set to False to allow multithreaded access required by SQLite in FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Factory configured for instantiating database session instances
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models in the application.
    """
    pass


def get_db():
    """
    Dependency generator that provides a transactional database session per request.
    Ensures the connection is closed after execution completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
