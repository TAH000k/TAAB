# app/schemas/notification.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    related_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    # Pydantic V2 configuration for SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
