from datetime import datetime
from pydantic import BaseModel
from app.models.borrow import BorrowStatus


class BorrowCreate(BaseModel):
    item_id: int
    due_date: datetime | None = None


class BorrowResolveDispute(BaseModel):
    target_status: BorrowStatus


class BorrowResponse(BaseModel):
    id: int
    item_id: int
    owner_id: int
    borrower_id: int

    status: BorrowStatus

    requested_at: datetime
    responded_at: datetime | None = None
    due_date: datetime | None = None

    borrowed_at: datetime | None = None
    returned_at: datetime | None = None

    lender_handover_confirmed_at: datetime | None = None
    borrower_handover_confirmed_at: datetime | None = None
    borrower_return_confirmed_at: datetime | None = None
    lender_return_confirmed_at: datetime | None = None

    class Config:
        from_attributes = True
