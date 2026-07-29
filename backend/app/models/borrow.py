import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import relationship

from app.database import Base


class BorrowStatus(str, enum.Enum):
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
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    borrower_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(Enum(BorrowStatus), default=BorrowStatus.PENDING, nullable=False)

    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    responded_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)

    borrowed_at = Column(DateTime, nullable=True)
    returned_at = Column(DateTime, nullable=True)

    lender_handover_confirmed_at = Column(DateTime, nullable=True)
    borrower_handover_confirmed_at = Column(DateTime, nullable=True)
    borrower_return_confirmed_at = Column(DateTime, nullable=True)
    lender_return_confirmed_at = Column(DateTime, nullable=True)

    item = relationship("Item", back_populates="borrows")
    owner = relationship("User", foreign_keys=[owner_id])
    borrower = relationship("User", foreign_keys=[borrower_id])

    __table_args__ = (
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
