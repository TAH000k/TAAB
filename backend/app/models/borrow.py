from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    Enum,
)

from sqlalchemy.orm import relationship

from app.database import Base

import enum


class BorrowStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BORROWED = "borrowed"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    LOST = "lost"


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    item_id = Column(
        Integer,
        ForeignKey("items.id"),
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    borrower_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        Enum(BorrowStatus),
        default=BorrowStatus.PENDING,
        nullable=False
    )

    requested_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    
    responded_at = Column(
        DateTime,
        nullable=True,
    )

    due_date = Column(
        DateTime,
        nullable=True
    )

    borrowed_at = Column(
        DateTime,
        nullable=True
    )

    returned_at = Column(
        DateTime,
        nullable=True
    )


    item = relationship(
        "Item",
        back_populates="borrows"
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="lent_items"
    )

    borrower = relationship(
        "User",
        foreign_keys=[borrower_id],
        back_populates="borrowed_items"
    )
