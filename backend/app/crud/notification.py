from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.notification import Notification

def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_id: Optional[int] = None
) -> Notification:
    """
    Create and store a new notification in the database.
    Note: 'db.commit()' is left to the calling router to preserve transaction integrity.
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_id=related_id
    )
    db.add(notification)
    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False
) -> List[Notification]:
    """
    Retrieve all notifications for a specific user.
    """
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).all()


def get_unread_count(db: Session, user_id: int) -> int:
    """
    Get the total count of unread notifications for a user.
    """
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()


def mark_as_read(
    db: Session,
    notification_id: int,
    user_id: int
) -> Optional[Notification]:
    """
    Mark a single notification as read if it belongs to the given user.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)

    return notification


def mark_all_as_read(db: Session, user_id: int) -> int:
    """
    Mark all unread notifications as read for a given user.
    Returns the number of updated records.
    """
    updated_count = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})

    db.commit()
    return updated_count
