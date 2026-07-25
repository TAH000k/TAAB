from sqlalchemy.orm import Session

from app.models.borrow import Borrow, BorrowStatus
from app.models.item import Item


def create_borrow_request(
    db: Session,
    item_id: int,
    borrower_id: int,
    due_date=None,
):
    item = (
        db.query(Item)
        .filter(Item.id == item_id)
        .first()
    )

    if item is None:
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
