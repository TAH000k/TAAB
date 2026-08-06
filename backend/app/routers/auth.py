"""
Authentication router module.
Provides API endpoints for user login (token generation) and fetching 
the current authenticated user's profile information.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud.user import authenticate_user
from app.auth import create_access_token

from app.auth import get_current_user
from app.models.user import User

from fastapi.security import OAuth2PasswordRequestForm

# Router configuration for authentication endpoints
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
def login(from_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates user credentials and returns a OAuth2-compatible Bearer access token.

    Args:
        from_data (OAuth2PasswordRequestForm): Form data containing username and password.
        db (Session): Injected database session.

    Returns:
        dict: JSON response containing the access token and token type.

    Raises:
        HTTPException: 401 UNAUTHORIZED if credentials are invalid.
    """
    # Authenticate credentials against the database
    user = authenticate_user(
        db=db,
        username=from_data.username,
        password=from_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Issue JWT access token with the user ID as subject
    access_token = create_access_token(
        {
            "sub": str(user.id),
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the currently authenticated user's details.

    Args:
        current_user (User): Authenticated user injected from the Bearer token.

    Returns:
        User: Currently logged-in user instance.
    """
    return current_user
