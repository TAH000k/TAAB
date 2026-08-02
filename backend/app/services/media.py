import os
import uuid
from fastapi import UploadFile, HTTPException, status

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def save_uploaded_file(file: UploadFile, folder: str) -> str:
    extension = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format"
        )

    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = os.path.join("uploads", folder)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return f"/static/{folder}/{unique_filename}"
