from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.borrow import BorrowCreate, BorrowResponse
from app.crud import borrow as borrow_crud

from app.auth import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/borrows",
    tags=["Borrows"]
)


@router.post(
    "/",
    response_model=BorrowResponse
)
def create_borrow_request(
    borrow: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = borrow_crud.create_borrow_request(
        db=db,
        item_id=borrow.item_id,
        borrower_id=current_user.id,
        due_date=borrow.due_date,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return result
