"""
Item service module.
Provides serialization functions to convert Item ORM models into ItemResponse schemas,
dynamically determining item availability based on active borrow records.
"""

from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.borrow import Borrow, BorrowStatus
from app.schemas.item import ItemResponse


# Borrow statuses that render an item unavailable for new borrow requests
UNAVAILABLE_STATUSES = [
    BorrowStatus.ACCEPTED,
    BorrowStatus.HANDOVER_PENDING,
    BorrowStatus.BORROWED,
    BorrowStatus.RETURN_PENDING,
    BorrowStatus.DISPUTED,
]


def serialize_item(db: Session, item: Item) -> ItemResponse:
    """
    Serializes a single Item model into an ItemResponse schema.
    Checks the database for active borrows to determine availability and current borrow ID.

    Args:
        db (Session): Database session context.
        item (Item): The Item ORM instance to serialize.

    Returns:
        ItemResponse: Pydantic response schema with computed availability status.
    """
    # Fetch active borrow associated with the item, if any exists
    active_borrow = (
        db.query(Borrow)
        .filter(
            Borrow.item_id == item.id,
            Borrow.status.in_(UNAVAILABLE_STATUSES),
        )
        .first()
    )

    return ItemResponse(
        id=item.id,
        owner_id=item.owner_id,
        name=item.name,
        description=item.description,
        category=item.category,
        image_url=item.image_url,
        available=active_borrow is None,
        current_borrow_id=active_borrow.id if active_borrow else None,
    )


def serialize_items(db: Session, items: list[Item]) -> list[ItemResponse]:
    """
    Serializes a list of Item models into ItemResponse schemas using batch processing.
    Optimized to prevent N+1 query performance issues when handling multiple items.

    Args:
        db (Session): Database session context.
        items (list[Item]): List of Item ORM instances.

    Returns:
        list[ItemResponse]: List of serialized Pydantic item response schemas.
    """
    if not items:
        return []

    item_ids = [item.id for item in items]

    # Query active borrows in batch for all items in the list
    active_borrows = (
        db.query(Borrow)
        .filter(
            Borrow.item_id.in_(item_ids),
            Borrow.status.in_(UNAVAILABLE_STATUSES),
        )
        .all()
    )

    # Map item IDs to their active borrow ID for O(1) lookups
    active_borrows_map = {b.item_id: b.id for b in active_borrows}

    return [
        ItemResponse(
            id=item.id,
            owner_id=item.owner_id,
            name=item.name,
            description=item.description,
            category=item.category,
            image_url=item.image_url,
            available=item.id not in active_borrows_map,
            current_borrow_id=active_borrows_map.get(item.id),
        )
        for item in items
    ]
