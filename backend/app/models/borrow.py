"""
Borrow database model and status enumeration.
Defines the Borrow ORM model for tracking item lending workflows,
including status state machine transitions and confirmation timestamps.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship

from app.database import Base


class BorrowStatus(str, enum.Enum):
    """
    Enumeration of lifecycle statuses for a borrow transaction.
    """
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    HANDOVER_PENDING = "HANDOVER_PENDING"
    BORROWED = "BORROWED"
    RETURN_PENDING = "RETURN_PENDING"
    RETURNED = "RETURNED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"
    DISPUTED = "DISPUTED"


class Borrow(Base):
    """
    SQLAlchemy model representing a borrow transaction between an item owner and a borrower.
    Includes milestone timestamps, handover/return verification steps, and partial unique indices.
    """
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(BorrowStatus), default=BorrowStatus.PENDING, nullable=False)

    # Initial request and schedule timestamps
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    responded_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    # Transaction lifecycle milestones
    borrowed_at = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)

    # Handover and return two-party verification timestamps
    lender_handover_confirmed_at = Column(DateTime, nullable=True)
    borrower_handover_confirmed_at = Column(DateTime, nullable=True)
    borrower_return_confirmed_at = Column(DateTime, nullable=True)
    lender_return_confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    item = relationship("Item", back_populates="borrows")
    owner = relationship("User", foreign_keys=[owner_id])
    borrower = relationship("User", foreign_keys=[borrower_id])

    __table_args__ = (
        # Partial unique index to enforce only one active borrow per item at a time
        Index(
            "idx_unique_active_borrow",
            "item_id",
            unique=True,
            sqlite_where=status.notin_([
                BorrowStatus.PENDING.value,
                BorrowStatus.RETURNED.value,
                BorrowStatus.REJECTED.value,
                BorrowStatus.CANCELED.value
            ])
        ),
    )
