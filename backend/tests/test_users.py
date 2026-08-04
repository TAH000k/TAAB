import pytest


def test_cannot_create_duplicate_username(client):
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
