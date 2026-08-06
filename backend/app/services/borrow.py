"""
Business logic service for managing item borrow workflows.
Handles state transitions, role validations, handover/return confirmations,
and dispute management for borrow transactions.
"""

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.borrow import Borrow, BorrowStatus


# List of borrow statuses indicating an active, unresolved transaction on an item
ACTIVE_BORROW_STATUSES = [
    BorrowStatus.ACCEPTED,
    BorrowStatus.HANDOVER_PENDING,
    BorrowStatus.BORROWED,
    BorrowStatus.RETURN_PENDING,
    BorrowStatus.DISPUTED,
]


def accept_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    """
    Accepts a pending borrow request for an item.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record to accept.
        current_user_id (int): ID of the requesting user.

    Returns:
        Borrow: Updated borrow record with ACCEPTED status.

    Raises:
        HTTPException: 403 if user is not the item owner.
        HTTPException: 400 if request status is not PENDING.
        HTTPException: 409 if item already has another active borrow.
    """
    # Ensure only the item owner can perform this action
    if borrow.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the item owner can accept this borrow request"
        )

    # Validate current request state
    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is no longer pending"
        )

    # Check for existing conflicting active borrows for the same item
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

    # Update status and record response timestamp
    borrow.status = BorrowStatus.ACCEPTED
    borrow.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(borrow)
    return borrow


def reject_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    """
    Rejects a pending borrow request.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record to reject.
        current_user_id (int): ID of the requesting user.

    Returns:
        Borrow: Updated borrow record with REJECTED status.

    Raises:
        HTTPException: 403 if user is not the item owner.
        HTTPException: 400 if request status is not PENDING.
    """
    # Ensure only the item owner can reject
    if borrow.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the item owner can reject this borrow request"
        )

    # Validate current request state
    if borrow.status != BorrowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is no longer pending"
        )

    # Update status and record response timestamp
    borrow.status = BorrowStatus.REJECTED
    borrow.responded_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(borrow)
    return borrow


def cancel_borrow_request(db: Session, borrow: Borrow, current_user_id: int) -> Borrow:
    """
    Cancels a borrow request prior to physical handover completion.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record to cancel.
        current_user_id (int): ID of the requesting user.

    Returns:
        Borrow: Updated borrow record with CANCELED status.

    Raises:
        HTTPException: 403 if user is neither owner nor borrower.
        HTTPException: 400 if handover is already completed.
    """
    # Validate authorization (must be involved party)
    if current_user_id not in [borrow.owner_id, borrow.borrower_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this borrow request"
        )

    # Ensure cancellation occurs before physical handover completes
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
    """
    Handles two-step confirmation for physical item handover.
    Step 1 (Owner): Transitions status to HANDOVER_PENDING.
    Step 2 (Borrower): Transitions status to BORROWED.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record.
        current_user_id (int): ID of the confirming party.

    Returns:
        Borrow: Updated borrow record.

    Raises:
        HTTPException: 400 if state transition is invalid.
        HTTPException: 403 if user is not a party to the transaction.
    """
    now = datetime.now(timezone.utc)

    # Step 1: Lender/Owner confirms item dispatch/handover initiation
    if current_user_id == borrow.owner_id:
        if borrow.status not in [BorrowStatus.ACCEPTED, BorrowStatus.HANDOVER_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Handover confirmation is not allowed in current status"
            )
        
        borrow.lender_handover_confirmed_at = now
        borrow.status = BorrowStatus.HANDOVER_PENDING

    # Step 2: Borrower confirms receipt of the item
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
    """
    Handles two-step confirmation for returning an item.
    Step 1 (Borrower): Transitions status to RETURN_PENDING.
    Step 2 (Owner): Transitions status to RETURNED.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record.
        current_user_id (int): ID of the confirming party.

    Returns:
        Borrow: Updated borrow record.

    Raises:
        HTTPException: 400 if state transition is invalid.
        HTTPException: 403 if user is not a party to the transaction.
    """
    now = datetime.now(timezone.utc)

    # Step 1: Borrower initiates return process
    if current_user_id == borrow.borrower_id:
        if borrow.status not in [BorrowStatus.BORROWED, BorrowStatus.RETURN_PENDING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return confirmation is not allowed in current status"
            )
        
        borrow.borrower_return_confirmed_at = now
        borrow.status = BorrowStatus.RETURN_PENDING

    # Step 2: Lender/Owner confirms receipt of returned item
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
    """
    Raises a dispute on an active or pending-confirmation borrow transaction.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record to dispute.
        current_user_id (int): ID of the party raising the dispute.

    Returns:
        Borrow: Updated borrow record with DISPUTED status.

    Raises:
        HTTPException: 403 if user is not a party to the transaction.
        HTTPException: 400 if borrow is not in a disputable stage.
    """
    if current_user_id not in [borrow.owner_id, borrow.borrower_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this borrow transaction"
        )

    # Disputes can only be raised during handover, active borrow, or return phases
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
    """
    Resolves an open dispute by resetting status to either BORROWED or RETURNED.

    Args:
        db (Session): Database session.
        borrow (Borrow): Borrow record.
        current_user_id (int): ID of the owner resolving the dispute.
        target_status (BorrowStatus): Destination status (BORROWED or RETURNED).

    Returns:
        Borrow: Updated borrow record with resolved status.

    Raises:
        HTTPException: 403 if user is not the owner.
        HTTPException: 400 if request is not disputed or target status is invalid.
    """
    # Only owner can resolve dispute
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

    # Target state validation
    if target_status not in [BorrowStatus.BORROWED, BorrowStatus.RETURNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved target status must be BORROWED or RETURNED"
        )

    borrow.status = target_status

    # Set timestamps if missing
    if target_status == BorrowStatus.RETURNED and not borrow.returned_at:
        borrow.returned_at = datetime.now(timezone.utc)
    elif target_status == BorrowStatus.BORROWED and not borrow.borrowed_at:
        borrow.borrowed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(borrow)
    return borrow
