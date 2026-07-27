from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.borrow import Borrow, BorrowStatus

from app.schemas.item import ItemResponse


def serialize_item(
    db: Session,
    item: Item,
) -> ItemResponse:

    active_borrow = (
        db.query(Borrow)
        .filter(
            Borrow.item_id == item.id,
            Borrow.status.in_(
                [
                    BorrowStatus.ACCEPTED,
                    BorrowStatus.BORROWED,
                ]
            ),
        )
        .first()
    )

    return ItemResponse(
        id=item.id,
        owner_id=item.owner_id,

        name=item.name,
        description=item.description,
        category=item.category,
        image=item.image,

        available=active_borrow is None,

        current_borrow_id=(
            active_borrow.id
            if active_borrow
            else None
        ),
    )


def serialize_items(
    db: Session,
    items: list[Item],
) -> list[ItemResponse]:

    return [
        serialize_item(
            db,
            item,
        )
        for item in items
    ]
