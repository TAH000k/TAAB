from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.item import Item
from app.schemas.item import ItemCreate
from app.models.group import Group, group_items, group_users

from typing import List

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
        .filter(Item.id == item_id, Item.is_deleted == False)
        .first()
    )


def get_user_items(
    db: Session,
    owner_id: int
):
    return (
        db.query(Item)
        .filter(Item.owner_id == owner_id, Item.is_deleted == False)
        .all()
    )


def search_items(db: Session, q: str):
    search_query = f"%{q}%"
    return db.query(Item).filter(
        Item.is_deleted == False,
        or_(
            Item.name.ilike(search_query),
            Item.description.ilike(search_query)
        )
    ).all()


def get_visible_items_by_user(db: Session, target_user_id: int, observer_id: int) -> List[Item]:
    if target_user_id == observer_id:
        return db.query(Item).filter(
            Item.owner_id == target_user_id,
            Item.is_deleted == False
        ).all()

    return db.query(Item).join(group_items).join(Group).join(group_users).filter(
        Item.owner_id == target_user_id,
        Item.is_deleted == False,
        Group.owner_id == target_user_id,
        group_users.c.user_id == observer_id
    ).distinct().all()


def delete_item(
    db: Session,
    item: Item
):
    item.is_deleted = True
    db.commit()
    db.refresh(item)
    return item
