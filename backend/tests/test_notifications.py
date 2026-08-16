"""
Integration tests for the notification system.
Tests retrieving notifications, unread counts, marking as read,
and verifying security (users cannot read others' notifications).
"""

import pytest


def get_auth_header(client, username: str, display_name: str) -> dict:
    client.post(
        "/users/",
        json={"username": username, "display_name": display_name, "password": "password123"},
    )
    response = client.post("/auth/login", data={"username": username, "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_sharing_users(client, owner_username, owner_name, borrower_username, borrower_name):
    # Register
    owner_res = client.post("/users/", json={"username": owner_username, "display_name": owner_name, "password": "password123"})
    owner_id = owner_res.json()["id"]

    borrower_res = client.post("/users/", json={"username": borrower_username, "display_name": borrower_name, "password": "password123"})
    borrower_id = borrower_res.json()["id"]

    # Login
    owner_login = client.post("/auth/login", data={"username": owner_username, "password": "password123"})
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    borrower_login = client.post("/auth/login", data={"username": borrower_username, "password": "password123"})
    borrower_headers = {"Authorization": f"Bearer {borrower_login.json()['access_token']}"}

    # Group
    group_res = client.post("/groups", json={"name": f"Test Group {owner_username}"}, headers=owner_headers)
    group_id = group_res.json()["id"]
    
    # Add User to Group
    client.post(f"/groups/{group_id}/users", json={"user_id": borrower_id}, headers=owner_headers)

    return owner_headers, borrower_headers, group_id


def test_borrow_request_creates_notification(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "notif_owner_1", "Owner One", "notif_borrower_1", "Borrower One"
    )

    # Create Item
    item_res = client.post(
        "/items/",
        json={"name": "Drill", "description": "Test drill", "category": "Tools"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]
    
    # Add Item to Group
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)

    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    notif_res = client.get("/notifications/", headers=owner_headers)
    assert notif_res.status_code == 200
    
    notifs = notif_res.json()
    assert isinstance(notifs, list)
    assert len(notifs) >= 1
    
    latest_notif = notifs[0]
    assert latest_notif["notification_type"] == "BORROW_REQUEST"
    assert latest_notif["is_read"] is False


def test_mark_notification_as_read(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "notif_owner_2", "Owner Two", "notif_borrower_2", "Borrower Two"
    )

    item_res = client.post("/items/", json={"name": "Camera"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)
    
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    notif_res = client.get("/notifications/", headers=owner_headers)
    notif_id = notif_res.json()[0]["id"]

    read_res = client.patch(f"/notifications/{notif_id}/read", headers=owner_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True


def test_cannot_read_others_notification(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "notif_owner_3", "Owner Three", "notif_borrower_3", "Borrower Three"
    )
    stranger_headers = get_auth_header(client, "stranger_1", "Stranger One")

    item_res = client.post("/items/", json={"name": "Laptop"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)
    
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    notif_res = client.get("/notifications/", headers=owner_headers)
    notif_id = notif_res.json()[0]["id"]

    read_res = client.patch(f"/notifications/{notif_id}/read", headers=stranger_headers)
    assert read_res.status_code in [403, 404]


def test_unread_notifications_count(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "notif_owner_4", "Owner Four", "notif_borrower_4", "Borrower Four"
    )

    initial_count_res = client.get("/notifications/unread-count", headers=owner_headers)
    assert initial_count_res.status_code == 200
    initial_count = initial_count_res.json().get("unread_count", 0)

    item_res = client.post("/items/", json={"name": "Projector"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)
    
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    new_count_res = client.get("/notifications/unread-count", headers=owner_headers)
    new_count = new_count_res.json().get("unread_count", 0)

    assert new_count == initial_count + 1
