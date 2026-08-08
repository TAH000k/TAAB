"""
User API router module.
Provides endpoints for user registration and profile picture updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import random
from pathlib import Path

from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import create_user, get_user_by_username
from app.models.user import User
from app.services.media import save_uploaded_file
from app.auth import get_current_user

# Router configuration for user management endpoints
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

dprofs=["dprof1.jpeg", "dprof2.jpg", "dprof3.jpg"]

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def delete_old_file_if_exists(file_path: str):
    if not file_path or (file_path in ["/static/defaults/dprof1.jpeg",
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
    Registers a new user in the system.

    Args:
        user (UserCreate): User creation payload containing registration details.
        db (Session): Injected database session.

    Returns:
        UserResponse: Created user profile details.

    Raises:
        HTTPException: 400 BAD REQUEST if the username is already taken.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    return create_user(db, user)


@router.post("/upload-profile_picture")
def upload_user_profile(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads and sets the profile picture for the currently authenticated user.

    Args:
        file (UploadFile): Uploaded image file object.
        db (Session): Injected database session.
        current_user (User): Authenticated user uploading the picture.

    Returns:
        dict: Object containing the relative profile picture URL.
    """
    db_user = get_user_by_username(db, username=current_user.username)

    delete_old_file_if_exists(db_user.profile_picture)
    
    profile_picture = save_uploaded_file(file, folder="users")
    db_user.profile_picture = profile_picture
    db.commit()
    db.refresh(db_user)

    return {"profile_picture": profile_picture}


@router.post("/reset-profile_picture")
def reset_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resets the profile picture for the currently authenticated user.

    Args:
        db (Session): Injected database session.
        current_user (User): Authenticated user.

    Returns:
        dict: Object containing the relative profile picture URL.
    """
    db_user = get_user_by_username(db, username=current_user.username)
        
    delete_old_file_if_exists(db_user.profile_picture)
            
    profile_picture = f"/static/defaults/{random.choice(dprofs)}"
    db_user.profile_picture = profile_picture
    db.commit()
    db.refresh(db_user)

    return {"profile_picture": profile_picture}
