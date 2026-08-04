from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.item import Item
from app.schemas.item import ItemCreate
from app.models.group import Group, group_items, group_users

from typing import List, Optional

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


def get_visible_item_by_id(db: Session, item_id: int, observer_id: int) -> Optional[Item]:
    accessible_item_ids = db.query(group_items.c.item_id).join(
        group_users, group_items.c.group_id == group_users.c.group_id
    ).filter(
        group_users.c.user_id == observer_id
    ).scalar_subquery()

    return db.query(Item).filter(
        Item.id == item_id,
        Item.is_deleted == False,
        or_(
            Item.owner_id == observer_id,
            Item.id.in_(accessible_item_ids)
        )
    ).first()


def get_user_items(
    db: Session,
    owner_id: int
):
    return (
        db.query(Item)
        .filter(Item.owner_id == owner_id, Item.is_deleted == False)
        .all()
    )


def search_visible_items(db: Session, query_str: str, observer_id: int) -> List[Item]:
    accessible_item_ids = db.query(group_items.c.item_id).join(
        group_users, group_items.c.group_id == group_users.c.group_id
    ).filter(
        group_users.c.user_id == observer_id
    ).scalar_subquery()

    search_pattern = f"%{query_str}%"

    return db.query(Item).filter(
        Item.is_deleted == False,
        or_(
            Item.name.ilike(search_pattern),
            Item.description.ilike(search_pattern)
        ),
        or_(
            Item.owner_id == observer_id,
            Item.id.in_(accessible_item_ids)
        )
    ).distinct().all()


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

def get_item(db: Session, item_id: int) -> Optional[Item]:
    return db.query(Item).filter(Item.id == item_id, Item.is_deleted == False).first()

def soft_delete_item(db: Session, db_item: Item) -> Item:
    db_item.is_deleted = True
    db.commit()
    db.refresh(db_item)
    return db_item
