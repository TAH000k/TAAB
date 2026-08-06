"""
Borrow API router module.
Provides endpoints for creating, retrieving, updating state, 
handling handovers, returns, disputes, and resolutions for item borrow requests.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.borrow import BorrowCreate, BorrowResponse, BorrowResolveDispute
from app.crud import borrow as borrow_crud
from app.services import borrow as borrow_service
from app.auth import get_current_user
from app.models.user import User

# Router configuration for borrow endpoints
router = APIRouter(prefix="/borrows", tags=["Borrows"])


@router.post("/", response_model=BorrowResponse, status_code=status.HTTP_201_CREATED)
def create_borrow_request(
    borrow: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new borrow request for a specific item.

    Args:
        borrow (BorrowCreate): Request payload containing item_id and optional due_date.
        db (Session): Injected database session.
        current_user (User): Authenticated user requesting the item.

    Returns:
        BorrowResponse: The created borrow request record.

    Raises:
        HTTPException: 400 BAD REQUEST if the borrow request cannot be created.
    """
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
    """
    Retrieves all borrow requests initiated by the current user.

    Args:
        db (Session): Injected database session.
        current_user (User): Authenticated borrower user.

    Returns:
        list[BorrowResponse]: List of sent borrow requests.
    """
    return borrow_crud.get_sent_requests(db=db, borrower_id=current_user.id)


@router.get("/received", response_model=list[BorrowResponse])
def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves all borrow requests received for items owned by the current user.

    Args:
        db (Session): Injected database session.
        current_user (User): Authenticated owner user.

    Returns:
        list[BorrowResponse]: List of received borrow requests.
    """
    return borrow_crud.get_received_requests(db=db, owner_id=current_user.id)


@router.post("/{borrow_id}/accept", response_model=BorrowResponse)
def accept_request(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts a pending borrow request (Item owner action).

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Rejects a pending borrow request (Item owner action).

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Cancels a borrow request before handover completion (Owner or Borrower action).

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Confirms physical item handover (Two-step process for owner and borrower).

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Confirms physical item return (Two-step process for borrower and owner).

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Raises a dispute on an active or pending borrow process.

    Args:
        borrow_id (int): ID of the borrow request.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request with DISPUTED status.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
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
    """
    Resolves an open dispute on a borrow request (Item owner action).

    Args:
        borrow_id (int): ID of the borrow request.
        payload (BorrowResolveDispute): Resolution target status payload.
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        BorrowResponse: Updated borrow request with resolved status.

    Raises:
        HTTPException: 404 NOT FOUND if the request does not exist.
    """
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
    return borrow_service.resolve_dispute(
        db=db,
        borrow=borrow,
        current_user_id=current_user.id,
        target_status=payload.target_status,
    )
