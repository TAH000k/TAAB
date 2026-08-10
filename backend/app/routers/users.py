"""
User API router module.
Provides endpoints for user registration and profile updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import random
from pathlib import Path
from typing import Optional
from app.crud import notification as notification_crud

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.crud.user import create_user, get_user_by_username
from app.models.user import User
from app.services.media import save_uploaded_file
from app.auth import get_current_user


# Router configuration for user management endpoints
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

dprofs = ["dprof1.jpeg", "dprof2.jpg", "dprof3.jpg"]

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def delete_old_file_if_exists(file_path: str):
    if not file_path or (file_path in [
        "/static/defaults/dprof1.jpeg",
        "/static/defaults/dprof2.jpg",
        "/static/defaults/dprof3.jpg"
    ]):
        return

    clean_relative_path = file_path.lstrip("/")
    full_path = (BASE_DIR / clean_relative_path).resolve()

    if full_path.exists() and full_path.is_file():
        os.remove(full_path)


@router.post("/", response_model=UserResponse)
def create_new_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registers a new user in the system and sends a welcome notification.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # 1. Create the user (this handles its own db.commit() and db.refresh())
    new_user = create_user(db, user)

    # 2. Create the welcome notification for the newly created user
    notification_crud.create_notification(
        db=db,
        user_id=new_user.id,
        title="Welcome to TAAB!",
        message="Welcome to TAAB! Start sharing and borrowing items with your friends and community.",
        notification_type="WELCOME",
        related_id=None
    )
    
    # 3. Commit the notification to the database
    db.commit()

    return new_user


@router.patch("/me", response_model=UserResponse)
def update_user_profile(
    display_name: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    reset_profile_picture: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the logged-in user's profile information (display_name, bio)
    and manage avatar (upload new file or reset to default).
    Note: Request body must be sent as `multipart/form-data`.
    """
    # 1. Update text fields if provided
    if display_name is not None:
        current_user.display_name = display_name
        
    if bio is not None:
        current_user.bio = bio

    # 2. Handle profile picture management
    if reset_profile_picture:
        # Case A: Reset to one of the random default profiles
        delete_old_file_if_exists(current_user.profile_picture)
        current_user.profile_picture = f"/static/defaults/{random.choice(dprofs)}"

    elif profile_picture and profile_picture.filename:
        # Case B: Upload a new profile picture using your media service
        delete_old_file_if_exists(current_user.profile_picture)
        
        # Saves the file and returns the relative path
        new_picture_url = save_uploaded_file(profile_picture, folder="users")
        current_user.profile_picture = new_picture_url

    # 3. Save updates to database
    current_user = db.merge(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user
