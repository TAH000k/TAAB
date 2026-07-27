from sqlalchemy.orm import Session

from app.models.borrow import Borrow, BorrowStatus
from app.models.item import Item

from datetime import datetime, timezone


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


def get_sent_requests(
    db: Session,
    borrower_id: int,
):
    return (
        db.query(Borrow)
        .filter(Borrow.borrower_id == borrower_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_received_requests(
    db: Session,
    owner_id: int,
):
    return (
        db.query(Borrow)
        .filter(Borrow.owner_id == owner_id)
        .order_by(Borrow.requested_at.desc())
        .all()
    )


def get_borrow_by_id(
    db: Session,
    borrow_id: int,
):
    return (
        db.query(Borrow)
        .filter(Borrow.id == borrow_id)
        .first()
    )


def accept_request(
    db: Session,
    borrow: Borrow,
):
    active_borrow = (
        db.query(Borrow)
        .filter(
            Borrow.item_id == borrow.item_id,
            Borrow.id != borrow.id,
            Borrow.status.in_(
                [
                    BorrowStatus.ACCEPTED,
                    BorrowStatus.BORROWED,
                ]
            ),
        )
        .first()
    )

    if active_borrow is not None:
        return None

    borrow.status = BorrowStatus.ACCEPTED
    borrow.responded_at = datetime.now(timezone.utc)

    (
        db.query(Borrow)
        .filter(
            Borrow.item_id == borrow.item_id,
            Borrow.id != borrow.id,
            Borrow.status == BorrowStatus.PENDING,
        )
        .update(
            {
                Borrow.status: BorrowStatus.REJECTED,
                Borrow.responded_at: datetime.now(timezone.utc),
            },
            synchronize_session=False,
        )
    )

    db.commit()
    db.refresh(borrow)

    return borrow


def reject_request(
    db: Session,
    borrow: Borrow,
):
    borrow.status = BorrowStatus.REJECTED
    borrow.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(borrow)

    return borrow
