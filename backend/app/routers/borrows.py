from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.borrow import BorrowCreate, BorrowResponse, BorrowResolveDispute
from app.crud import borrow as borrow_crud
from app.services import borrow as borrow_service
from app.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/borrows", tags=["Borrows"])


@router.post("/", response_model=BorrowResponse, status_code=status.HTTP_201_CREATED)
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create borrow request for this item"
        )
    return result


@router.get("/sent", response_model=list[BorrowResponse])
def get_sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return borrow_crud.get_sent_requests(db=db, borrower_id=current_user.id)


@router.get("/received", response_model=list[BorrowResponse])
def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return borrow_crud.get_received_requests(db=db, owner_id=current_user.id)


@router.post("/{borrow_id}/accept", response_model=BorrowResponse)
def accept_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.accept_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/reject", response_model=BorrowResponse)
def reject_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.reject_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/cancel", response_model=BorrowResponse)
def cancel_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.cancel_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/handover", response_model=BorrowResponse)
def confirm_handover(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.confirm_handover(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/return", response_model=BorrowResponse)
def confirm_return(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.confirm_return(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/dispute", response_model=BorrowResponse)
def raise_dispute(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.raise_dispute(db=db, borrow=borrow, current_user_id=current_user.id)


@router.post("/{borrow_id}/resolve-dispute", response_model=BorrowResponse)
def resolve_dispute(
    borrow_id: int,
    payload: BorrowResolveDispute,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.resolve_dispute(
        db=db,
        borrow=borrow,
        current_user_id=current_user.id,
        target_status=payload.target_status,
    )
