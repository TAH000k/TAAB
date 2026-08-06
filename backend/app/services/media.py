"""
Media handling service module.
Provides file upload utility functions, file extension validation,
and secure file storage management.
"""

import os
import uuid
from fastapi import UploadFile, HTTPException, status

# Allowed image file extensions for uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def save_uploaded_file(file: UploadFile, folder: str) -> str:
    """
    Validates, saves an uploaded file to disk with a unique filename,
    and returns its accessible static URL path.

    Args:
        file (UploadFile): Injected file object from the request.
        folder (str): Target subfolder within the uploads directory.

    Returns:
        str: Relative static URL path for accessing the saved file.

    Raises:
        HTTPException: 400 BAD REQUEST if the file extension is not allowed.
    """
    # Extract and validate file extension
    extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format"
        )

    # Generate a unique UUID-based filename to prevent naming collisions
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = os.path.join("uploads", folder)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_filename)

    # Write file stream content to disk
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return f"/static/{folder}/{unique_filename}"
