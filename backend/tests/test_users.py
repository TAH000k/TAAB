"""
Integration tests for user registration and management endpoints.
Verifies user creation constraints such as duplicate username prevention.
"""

import pytest


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
