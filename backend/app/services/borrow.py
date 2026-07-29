from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.borrow import Borrow, BorrowStatus


ACTIVE_BORROW_STATUSES = [
    BorrowStatus.ACCEPTED,
    BorrowStatus.HANDOVER_PENDING,
    BorrowStatus.BORROWED,
    BorrowStatus.RETURN_PENDING,
    BorrowStatus.DISPUTED,
]


def accept_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    if borrow.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the item owner can accept this borrow request"
        )

    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is no longer pending"
        )

    active_borrow = db.query(Borrow).filter(
        Borrow.item_id == borrow.item_id,
        Borrow.id != borrow.id,
        Borrow.status.in_(ACTIVE_BORROW_STATUSES)
    ).first()

    if active_borrow:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This item currently has an active borrow request"
        )

    borrow.status = BorrowStatus.ACCEPTED
    borrow.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(borrow)
    return borrow


def reject_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    if borrow.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the item owner can reject this borrow request"
        )

    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is no longer pending"
        )

    borrow.status = BorrowStatus.REJECTED
    borrow.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(borrow)
    return borrow


def cancel_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    if current_user_id not in [borrow.owner_id, borrow.borrower_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this borrow request"
        )

    if borrow.status not in [BorrowStatus.PENDING, BorrowStatus.ACCEPTED, BorrowStatus.HANDOVER_PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow process cannot be canceled after handover is completed"
        )

    borrow.status = BorrowStatus.CANCELED
    db.commit()
    db.refresh(borrow)
    return borrow


def confirm_handover(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    now = datetime.now(timezone.utc)

    if current_user_id == borrow.owner_id:
        if borrow.status not in [BorrowStatus.ACCEPTED, BorrowStatus.HANDOVER_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Handover confirmation is not allowed in current status"
            )
        
        borrow.lender_handover_confirmed_at = now
        borrow.status = BorrowStatus.HANDOVER_PENDING

    elif current_user_id == borrow.borrower_id:
        if borrow.status != BorrowStatus.HANDOVER_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner must confirm handover before borrower confirmation"
            )
        
        borrow.borrower_handover_confirmed_at = now
        borrow.status = BorrowStatus.BORROWED
        borrow.borrowed_at = now
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this borrow transaction"
        )

    db.commit()
    db.refresh(borrow)
    return borrow


def confirm_return(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    now = datetime.now(timezone.utc)

    if current_user_id == borrow.borrower_id:
        if borrow.status not in [BorrowStatus.BORROWED, BorrowStatus.RETURN_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return confirmation is not allowed in current status"
            )
        
        borrow.borrower_return_confirmed_at = now
        borrow.status = BorrowStatus.RETURN_PENDING

    elif current_user_id == borrow.owner_id:
        if borrow.status != BorrowStatus.RETURN_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Borrower must confirm return before owner confirmation"
            )
        
        borrow.lender_return_confirmed_at = now
        borrow.status = BorrowStatus.RETURNED
        borrow.returned_at = now
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this borrow transaction"
        )

    db.commit()
    db.refresh(borrow)
    return borrow


def raise_dispute(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    if current_user_id not in [borrow.owner_id, borrow.borrower_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this borrow transaction"
        )

    if borrow.status not in [BorrowStatus.HANDOVER_PENDING, BorrowStatus.RETURN_PENDING, BorrowStatus.BORROWED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dispute cannot be raised at this stage"
        )

    borrow.status = BorrowStatus.DISPUTED
    db.commit()
    db.refresh(borrow)
    return borrow


def resolve_dispute(db: Session, borrow: Borrow, current_user_id: int, target_status: BorrowStatus) -> Borrow:
    if current_user_id != borrow.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the item owner can resolve this dispute"
        )

    if borrow.status != BorrowStatus.DISPUTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is not in DISPUTED status"
        )

    if target_status not in [BorrowStatus.BORROWED, BorrowStatus.RETURNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved target status must be BORROWED or RETURNED"
        )

    borrow.status = target_status
    if target_status == BorrowStatus.RETURNED and not borrow.returned_at:
        borrow.returned_at = datetime.now(timezone.utc)
    elif target_status == BorrowStatus.BORROWED and not borrow.borrowed_at:
        borrow.borrowed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(borrow)
    return borrow
