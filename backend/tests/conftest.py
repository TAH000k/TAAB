"""
Pytest configuration and test fixtures module.
Provides an isolated, in-memory SQLite database session and a FastAPI TestClient
configured with dependency overrides for automated testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db as db_get_db
from app.dependencies import get_db as dep_get_db

# In-memory SQLite database configuration for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Creates fresh database schema and yields an isolated SQLAlchemy session for each test.
    Drops all tables after execution to guarantee test independence.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Yields a FastAPI TestClient instance configured with database dependency overrides.

    Args:
        db_session: Isolated SQLAlchemy test session fixture.

    Yields:
        TestClient: FastAPI test client with database dependency overrides.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Overriding both database and dependency get_db sources
    app.dependency_overrides[db_get_db] = override_get_db
    app.dependency_overrides[dep_get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
