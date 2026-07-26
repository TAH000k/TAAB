from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.borrow import BorrowCreate, BorrowResponse
from app.crud import borrow as borrow_crud

from app.auth import get_current_user
from app.models.user import User

from app.models.borrow import BorrowStatus


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


@router.get(
    "/sent",
    response_model=list[BorrowResponse],
)
def get_sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return borrow_crud.get_sent_requests(
        db=db,
        borrower_id=current_user.id,
    )
    

@router.get(
    "/received",
    response_model=list[BorrowResponse],
)
def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return borrow_crud.get_received_requests(
        db=db,
        owner_id=current_user.id,
    )


@router.post(
    "/{borrow_id}/accept",
    response_model=BorrowResponse,
)
def accept_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(
        db=db,
        borrow_id=borrow_id,
    )

    if borrow is None:
        raise HTTPException(
            status_code=404,
            detail="Borrow request not found",
        )

    if borrow.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this item",
        )

    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Borrow request is no longer pending",
        )

    return borrow_crud.accept_request(
        db=db,
        borrow=borrow,
    )
    

@router.post(
    "/{borrow_id}/reject",
    response_model=BorrowResponse,
)
def reject_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(
        db=db,
        borrow_id=borrow_id,
    )

    if borrow is None:
        raise HTTPException(
            status_code=404,
            detail="Borrow request not found",
        )

    if borrow.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this item",
        )

    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Borrow request is no longer pending",
        )

    return borrow_crud.reject_request(
        db=db,
        borrow=borrow,
    )
