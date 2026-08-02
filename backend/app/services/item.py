from sqlalchemy.orm import Session
from app.models.item import Item
from app.models.borrow import Borrow, BorrowStatus
from app.schemas.item import ItemResponse


UNAVAILABLE_STATUSES = [
    BorrowStatus.ACCEPTED,
    BorrowStatus.HANDOVER_PENDING,
    BorrowStatus.BORROWED,
    BorrowStatus.RETURN_PENDING,
    BorrowStatus.DISPUTED,
]


def serialize_item(db: Session, item: Item) -> ItemResponse:
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
    if not items:
        return []

    item_ids = [item.id for item in items]

    active_borrows = (
        db.query(Borrow)
        .filter(
            Borrow.item_id.in_(item_ids),
            Borrow.status.in_(UNAVAILABLE_STATUSES),
        )
        .all()
    )

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
