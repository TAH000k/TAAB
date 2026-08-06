"""
Item database model module.
Defines the Item ORM model representing user-owned items available for borrowing,
including soft-deletion status and relationship mappings.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Item(Base):
    """
    SQLAlchemy model representing an item listed in the system.
    Tracks metadata, ownership, creation timestamps, soft-deletion flag,
    and associated borrow transaction histories.
    """
    __tablename__ = "items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )

    category = Column(
        String(50),
        nullable=True
    )

    image_url = Column(
        String, 
        nullable=True
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    
    is_deleted = Column(
        Boolean, 
        default=False, 
        nullable=False
    )

    # Relationships
    owner = relationship(
        "User",
        back_populates="items"
    )
    
    borrows = relationship(
        "Borrow",
        back_populates="item"
    )
