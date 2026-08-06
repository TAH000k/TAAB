"""
Pydantic schemas for borrow-related API requests and responses.
Defines data validation models for creating borrow requests, resolving disputes,
and returning structured borrow transaction details.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.borrow import BorrowStatus


class BorrowCreate(BaseModel):
    """
    Schema for creating a new borrow request.
    """
    item_id: int
    due_date: datetime | None = None


class BorrowResolveDispute(BaseModel):
    """
    Schema for defining the resolution target status of a disputed borrow transaction.
    """
    target_status: BorrowStatus


class BorrowResponse(BaseModel):
    """
    Response model representing a detailed borrow transaction record.
    """
    id: int
    item_id: int
    owner_id: int
    borrower_id: int

    status: BorrowStatus

    # Request timestamps and schedule
    requested_at: datetime
    responded_at: datetime | None = None
    due_date: datetime | None = None

    # Lifecycle milestones
    borrowed_at: datetime | None = None
    returned_at: datetime | None = None

    # Handover and return confirmation timestamps
    lender_handover_confirmed_at: datetime | None = None
    borrower_handover_confirmed_at: datetime | None = None
    borrower_return_confirmed_at: datetime | None = None
    lender_return_confirmed_at: datetime | None = None

    # Enable ORM mode for compatibility with SQLAlchemy model attributes
    model_config = ConfigDict(from_attributes=True)
