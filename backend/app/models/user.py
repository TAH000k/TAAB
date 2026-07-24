from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base

from enum import Enum
from sqlalchemy import Enum as SQLEnum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    
    
class User(Base):
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
    