"""
Group CRUD operations module.
Provides database access functions for creating groups and managing group memberships for users and items.
"""

from sqlalchemy.orm import Session
from app.models.group import Group
from app.models.user import User
from app.models.item import Item


def create_group(db: Session, name: str, owner_id: int) -> Group:
    """
    Creates a new group record.

    Args:
        db (Session): Injected database session.
        name (str): Name of the new group.
        owner_id (int): ID of the user who owns the group.

    Returns:
        Group: The newly created Group database instance.
    """
    group = Group(name=name, owner_id=owner_id)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def add_user_to_group(db: Session, group: Group, user: User) -> Group:
    """
    Adds a user to a group if they are not already a member.

    Args:
        db (Session): Injected database session.
        group (Group): The group instance to update.
        user (User): The user instance to add to the group.

    Returns:
        Group: The updated group instance.
    """
    if user not in group.users:
        group.users.append(user)
        db.commit()
        db.refresh(group)
    return group


def add_item_to_group(db: Session, group: Group, item: Item) -> Group:
    """
    Associates an item with a group if it is not already added.

    Args:
        db (Session): Injected database session.
        group (Group): The group instance to update.
        item (Item): The item instance to associate with the group.

    Returns:
        Group: The updated group instance.
    """
    if item not in group.items:
        group.items.append(item)
        db.commit()
        db.refresh(group)
    return group
