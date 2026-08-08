"""
Integration tests for user registration and management endpoints.
Verifies user creation constraints such as duplicate username prevention.
"""

import pytest
from fastapi import status

from tests.conftest import client
from tests.test_borrow_flow import get_auth_header

def test_cannot_create_duplicate_username(client):
    """
    Tests that attempting to register a user with an already existing username fails.
    Verifies that a 400 Bad Request status code and the expected error message are returned.
    """
    user_data = {
        "username": "unique_guy",
        "display_name": "First User",
        "password": "password123"
    }

    first_res = client.post("/users/", json=user_data)
    assert first_res.status_code == 200

    duplicate_res = client.post(
        "/users/",
        json={
            "username": "unique_guy",
            "display_name": "Imposter User",
            "password": "password123"
        }
    )

    assert duplicate_res.status_code == 400
    assert duplicate_res.json()["detail"] == "Username already registered"


def test_update_user_profile_text_fields(client, db_session):
    headers = get_auth_header(client, "patchuser", "Old Display Name")
    
    update_data = {
        "display_name": "Updated Name",
        "bio": "This is my new bio!"
    }
    response = client.patch("/users/me", headers=headers, data=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["display_name"] == "Updated Name"
    assert data["bio"] == "This is my new bio!"


def test_update_user_profile_picture_upload(client, db_session, tmp_path):
    headers = get_auth_header(client, "picuser", "Pic User")

    dummy_image_path = tmp_path / "test_avatar.jpg"
    dummy_image_path.write_bytes(b"fake image content")

    with open(dummy_image_path, "rb") as img_file:
        files = {
            "profile_picture": ("test_avatar.jpg", img_file, "image/jpeg")
        }
        response = client.patch("/users/me", headers=headers, files=files)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["profile_picture"] is not None
    assert "/static/uploads/users/" in data["profile_picture"]


def test_update_user_profile_reset_picture(client, db_session):
    headers = get_auth_header(client, "resetuser", "Reset User")
    
    update_data = {
        "reset_profile_picture": "true"
    }
    response = client.patch("/users/me", headers=headers, data=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    valid_defaults = [
        "/static/defaults/dprof1.jpeg",
        "/static/defaults/dprof2.jpg",
        "/static/defaults/dprof3.jpg"
    ]
    assert data["profile_picture"] in valid_defaults