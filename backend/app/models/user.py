"""
User database model and role enumeration module.
Defines the User ORM model representing registered accounts, user roles,
and relationship mappings to owned items and borrow records.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    """
    Enumeration of system authorization roles.
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    SQLAlchemy model representing a registered user account.
    Stores credentials, profile details, access role, and associations
    with owned items as well as lent and borrowed transactions.
    """
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(32),
        unique=True,
        nullable=False,
        index=True
    )

    display_name = Column(
        String(64),
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    profile_picture = Column(
        String,
        nullable=True
    )

    bio = Column(
        String(300),
        nullable=True
    )

    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.USER
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    items = relationship(
        "Item",
        back_populates="owner"
    )

    lent_items = relationship(
        "Borrow",
        foreign_keys="Borrow.owner_id",
        back_populates="owner"
    )

    borrowed_items = relationship(
        "Borrow",
        foreign_keys="Borrow.borrower_id",
        back_populates="borrower"
    )
