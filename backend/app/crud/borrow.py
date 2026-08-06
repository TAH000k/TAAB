"""
Borrow CRUD operations module.
Provides database access functions for creating, querying, and retrieving borrow requests.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.borrow import Borrow, BorrowStatus
from app.models.item import Item


def create_borrow_request(
    db: Session, 
    item_id: int, 
    borrower_id: int, 
    due_date=None
) -> Optional[Borrow]:
    """
    Creates a new borrow request for a specified item.

    Args:
        db (Session): Injected database session.
        item_id (int): ID of the item to borrow.
        borrower_id (int): ID of the user requesting to borrow the item.
        due_date (datetime, optional): Proposed return date for the borrow request.

    Returns:
        Optional[Borrow]: The created Borrow record, or None if the item does not exist 
                          or if the borrower is the owner of the item.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        return None

    if item.owner_id == borrower_id:
        return None

    borrow = Borrow(
        item_id=item.id,
        owner_id=item.owner_id,
        borrower_id=borrower_id,
        status=BorrowStatus.PENDING,
        due_date=due_date,
    )

    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return borrow


def get_sent_requests(db: Session, borrower_id: int) -> List[Borrow]:
    """
    Retrieves all borrow requests initiated by a specific borrower, ordered by request date descending.

    Args:
        db (Session): Injected database session.
        borrower_id (int): ID of the borrower user.

    Returns:
        List[Borrow]: List of borrow requests sent by the user.
    """
    return (
        db.query(Borrow)
        .filter(Borrow.borrower_id == borrower_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_received_requests(db: Session, owner_id: int) -> List[Borrow]:
    """
    Retrieves all borrow requests received for items owned by a specific user, ordered by request date descending.

    Args:
        db (Session): Injected database session.
        owner_id (int): ID of the item owner user.

    Returns:
        List[Borrow]: List of borrow requests received by the user.
    """
    return (
        db.query(Borrow)
        .filter(Borrow.owner_id == owner_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_borrow_by_id(db: Session, borrow_id: int) -> Optional[Borrow]:
    """
    Retrieves a single borrow request record by its unique database identifier.

    Args:
        db (Session): Injected database session.
        borrow_id (int): ID of the borrow request.

    Returns:
        Optional[Borrow]: The Borrow record if found, otherwise None.
    """
    return db.query(Borrow).filter(Borrow.id == borrow_id).first()
