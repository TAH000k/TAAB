from sqlalchemy.orm import Session
from app.models.group import Group
from app.models.user import User
from app.models.item import Item

def create_group(db: Session, name: str, owner_id: int) -> Group:
    group = Group(name=name, owner_id=owner_id)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

def add_user_to_group(db: Session, group: Group, user: User) -> Group:
    if user not in group.users:
        group.users.append(user)
        db.commit()
        db.refresh(group)
    return group

def add_item_to_group(db: Session, group: Group, item: Item) -> Group:
    if item not in group.items:
        group.items.append(item)
        db.commit()
        db.refresh(group)
    return group
