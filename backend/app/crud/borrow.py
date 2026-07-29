from sqlalchemy.orm import Session
from app.models.borrow import Borrow, BorrowStatus
from app.models.item import Item


def create_borrow_request(db: Session, item_id: int, borrower_id: int, due_date=None):
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


def get_sent_requests(db: Session, borrower_id: int):
    return (
        db.query(Borrow)
        .filter(Borrow.borrower_id == borrower_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_received_requests(db: Session, owner_id: int):
    return (
        db.query(Borrow)
        .filter(Borrow.owner_id == owner_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_borrow_by_id(db: Session, borrow_id: int):
    return db.query(Borrow).filter(Borrow.id == borrow_id).first()
