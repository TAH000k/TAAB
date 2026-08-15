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
from app.crud import notification as notification_crud
from app.crud import item as item_crud
from app.crud.user import get_user_by_id
from app.crud.item import get_item
from app.services import borrow as borrow_service
from app.auth import get_current_user
from app.models.user import User


# Router configuration for borrow endpoints
router = APIRouter(prefix="/borrows", tags=["Borrows"])


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


@router.post("/", response_model=BorrowResponse, status_code=status.HTTP_201_CREATED)
def create_borrow_request(
    borrow: BorrowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new borrow request for a specific item.
    """
    item = item_crud.get_visible_item_by_id(db, item_id=borrow.item_id, observer_id=current_user.id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you don't have access to it"
        )
        
    if item.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot borrow your own item."
        )

    result = borrow_crud.create_borrow_request(
        db=db,
        item_id=borrow.item_id,
        borrower_id=current_user.id,
        due_date=borrow.due_date,
    )
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create borrow request for this item. It might be unavailable."
        )
    
    notification_crud.create_notification(
        db=db,
        user_id=item.owner_id,
        title="New Borrow Request",
        message=f"{current_user.display_name} ({current_user.username}) requested to borrow '{item.name}' ({item.id}).",
        notification_type="BORROW_REQUEST",
        related_id=result.id
    )
    
    return result


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
    
    updated_borrow = borrow_service.accept_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    notification_crud.create_notification(
        db=db,
        user_id=borrow.borrower_id,
        title="Request Accepted!",
        message=f"Your request to borrow '{item.name}'({item.id}) has been accepted. Arrange the handover with the owner.",
        notification_type="BORROW_ACCEPTED",
        related_id=borrow.id
    )
    
    return updated_borrow


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
    
    updated_borrow = borrow_service.reject_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    notification_crud.create_notification(
        db=db,
        user_id=borrow.borrower_id,
        title="Request Declined",
        message=f"Your request to borrow '{item.name}' was declined by the owner.",
        notification_type="BORROW_REJECTED",
        related_id=borrow.id
    )
    
    return updated_borrow


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
    
    updated_borrow = borrow_service.cancel_borrow_request(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    notification_crud.create_notification(
        db=db,
        user_id=item.owner_id,
        title="Request Cancelled",
        message=f"{current_user.display_name}({current_user.username}) cancelled their request for '{item.name}'({item.id}).",
        notification_type="BORROW_CANCELLED",
        related_id=borrow.id
    )
    
    return updated_borrow


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
    
    updated_borrow = borrow_service.confirm_handover(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    if current_user.id == item.owner_id:
        notification_crud.create_notification(
            db=db,
            user_id=borrow.borrower_id,
            title="Handover Initiated",
            message=f"The owner marked '{item.name}'({item.id}) as handed over. Please confirm when you receive it.",
            notification_type="HANDOVER_PENDING",
            related_id=borrow.id
        )
    else:
        notification_crud.create_notification(
            db=db,
            user_id=item.owner_id,
            title="Handover Confirmed",
            message=f"{current_user.display_name or current_user.username} confirmed receiving '{item.name}'({item.id}). Item status is now Borrowed.",
            notification_type="HANDOVER_CONFIRMED",
            related_id=borrow.id
        )
    
    return updated_borrow


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
    
    updated_borrow = borrow_service.confirm_return(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    if current_user.id == borrow.borrower_id:
        notification_crud.create_notification(
            db=db,
            user_id=item.owner_id,
            title="Item Returned",
            message=f"{current_user.display_name or current_user.username} marked '{item.name}'({item.id}) as returned. Please confirm receipt.",
            notification_type="RETURN_PENDING",
            related_id=borrow.id
        )
    else:
        notification_crud.create_notification(
            db=db,
            user_id=borrow.borrower_id,
            title="Return Confirmed",
            message=f"The owner confirmed receiving '{item.name}'({item.id}). The borrowing period is now completed!",
            notification_type="RETURN_CONFIRMED",
            related_id=borrow.id
        )
    
    return updated_borrow


@router.post("/{borrow_id}/dispute", response_model=BorrowResponse)
def raise_dispute(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Raises a dispute on an active or pending borrow process.
    """
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
        
    updated_borrow = borrow_service.raise_dispute(db=db, borrow=borrow, current_user_id=current_user.id)
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    target_user_id = item.owner_id if current_user.id == borrow.borrower_id else borrow.borrower_id
    
    notification_crud.create_notification(
        db=db,
        user_id=target_user_id,
        title="Dispute Raised",
        message=f"{current_user.display_name or current_user.username} raised a dispute regarding '{item.name}'({item.id}).",
        notification_type="DISPUTE_RAISED",
        related_id=borrow.id
    )
    
    return updated_borrow


@router.post("/{borrow_id}/resolve-dispute", response_model=BorrowResponse)
def resolve_dispute(
    borrow_id: int,
    payload: BorrowResolveDispute,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Resolves an open dispute on a borrow request (Item owner action).
    """
    borrow = borrow_crud.get_borrow_by_id(db=db, borrow_id=borrow_id)
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow request not found")
        
    updated_borrow = borrow_service.resolve_dispute(
        db=db,
        borrow=borrow,
        current_user_id=current_user.id,
        target_status=payload.target_status,
    )
    
    item = get_item(db=db, item_id=borrow.item_id)
    
    notification_crud.create_notification(
        db=db,
        user_id=borrow.borrower_id,
        title="Dispute Resolved",
        message=f"The dispute for '{item.name}'({item.id}) has been resolved. New status: {payload.target_status}",
        notification_type="DISPUTE_RESOLVED",
        related_id=borrow.id
    )
    
    return updated_borrow
