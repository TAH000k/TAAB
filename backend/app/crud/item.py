from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate


def create_item(
    db: Session,
    item_data: ItemCreate,
    owner_id: int
):
    item = Item(
        name=item_data.name,
        description=item_data.description,
        category=item_data.category,
        owner_id=owner_id
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


def get_item(
    db: Session,
    item_id: int
):
    return (
        db.query(Item)
        .filter(Item.id == item_id)
        .first()
    )


def get_user_items(
    db: Session,
    owner_id: int
):
    return (
        db.query(Item)
        .filter(Item.owner_id == owner_id)
        .all()
    )


def delete_item(
    db: Session,
    item: Item
):
    db.delete(item)
    db.commit()
