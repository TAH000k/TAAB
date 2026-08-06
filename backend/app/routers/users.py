"""
User API router module.
Provides endpoints for user registration and profile picture updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

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
def upload_user_image(
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

    profile_picture = save_uploaded_file(file, folder="users")
    db_user.profile_picture = profile_picture
    db.commit()
    db.refresh(db_user)

    return {"profile_picture": profile_picture}
