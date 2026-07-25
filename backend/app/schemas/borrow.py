from datetime import datetime

from pydantic import BaseModel

from app.models.borrow import BorrowStatus


class BorrowCreate(BaseModel):
    item_id: int
    due_date: datetime | None = None


class BorrowResponse(BaseModel):
    id: int

    item_id: int
    owner_id: int
    borrower_id: int

    status: BorrowStatus

    requested_at: datetime
    due_date: datetime | None

    borrowed_at: datetime | None
    returned_at: datetime | None

    class Config:
        from_attributes = True
