"""
User CRUD operations module.
Provides database access functions for creating users, querying user records,
and authenticating user credentials.
"""

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Creates and saves a new user record with a hashed password.

    Args:
        db (Session): Injected database session.
        user_data (UserCreate): Schema containing registration details.

    Returns:
        User: The newly created User database instance.
    """
    user = User(
        username=user_data.username,
        display_name=user_data.display_name,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Retrieves a user by their unique username.

    Args:
        db (Session): Injected database session.
        username (str): Username to search for.

    Returns:
        Optional[User]: The User instance if found, otherwise None.
    """
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by their primary key database ID.

    Args:
        db (Session): Injected database session.
        user_id (int): Unique database ID of the user.

    Returns:
        Optional[User]: The User instance if found, otherwise None.
    """
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticates a user by verifying their username and plain-text password.

    Args:
        db (Session): Injected database session.
        username (str): Username of the account.
        password (str): Plain-text password attempt.

    Returns:
        Optional[User]: The authenticated User instance if valid, otherwise None.
    """
    user = get_user_by_username(db, username)

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
