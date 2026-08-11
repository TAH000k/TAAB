"""
Integration tests for the notification system.
Tests retrieving notifications, unread counts, marking as read,
and verifying security (users cannot read others' notifications).
"""

import pytest


def get_auth_header(client, username: str, display_name: str) -> dict:
    """
    Helper function to register a test user, log in, and return HTTP authorization headers.
    """
    client.post(
        "/users/",
        json={
            "username": username,
            "display_name": display_name,
            "password": "password123",
        },
    )
    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": "password123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_borrow_request_creates_notification(client):
    """
    Tests that a borrow request correctly generates a notification for the item owner.
    """
    owner_headers = get_auth_header(client, "notif_owner_1", "Owner One")
    borrower_headers = get_auth_header(client, "notif_borrower_1", "Borrower One")

    # 1. Owner creates an item
    item_res = client.post(
        "/items/",
        json={"name": "Drill", "description": "Test drill", "category": "Tools"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]

    # 2. Borrower requests the item
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    # 3. Check owner's notifications
    notif_res = client.get("/notifications/", headers=owner_headers)
    assert notif_res.status_code == 200
    
    notifs = notif_res.json()
    assert isinstance(notifs, list)
    assert len(notifs) >= 1
    
    # The most recent notification should be the borrow request
    latest_notif = notifs[0]
    assert latest_notif["notification_type"] == "BORROW_REQUEST"
    assert latest_notif["is_read"] is False


def test_mark_notification_as_read(client):
    """
    Tests that a user can successfully mark their own notification as read.
    """
    owner_headers = get_auth_header(client, "notif_owner_2", "Owner Two")
    borrower_headers = get_auth_header(client, "notif_borrower_2", "Borrower Two")

    # Trigger a notification
    item_res = client.post("/items/", json={"name": "Camera"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    # Fetch the generated notification ID
    notif_res = client.get("/notifications/", headers=owner_headers)
    notif_id = notif_res.json()[0]["id"]

    # Mark as read (Assuming the endpoint is PATCH /notifications/{id}/read)
    read_res = client.patch(f"/notifications/{notif_id}/read", headers=owner_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True


def test_cannot_read_others_notification(client):
    """
    Security test: A user cannot mark another user's notification as read.
    """
    owner_headers = get_auth_header(client, "notif_owner_3", "Owner Three")
    borrower_headers = get_auth_header(client, "notif_borrower_3", "Borrower Three")
    stranger_headers = get_auth_header(client, "stranger_1", "Stranger One")

    # Trigger a notification for the owner
    item_res = client.post("/items/", json={"name": "Laptop"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    notif_res = client.get("/notifications/", headers=owner_headers)
    notif_id = notif_res.json()[0]["id"]

    # Stranger attempts to mark the owner's notification as read
    read_res = client.patch(f"/notifications/{notif_id}/read", headers=stranger_headers)
    
    # Should be rejected with a 404 Not Found or 403 Forbidden
    assert read_res.status_code in [403, 404]


def test_unread_notifications_count(client):
    """
    Tests that the unread notifications count increments correctly.
    """
    owner_headers = get_auth_header(client, "notif_owner_4", "Owner Four")
    borrower_headers = get_auth_header(client, "notif_borrower_4", "Borrower Four")

    # Get initial count (might be > 0 if there's a welcome notification upon signup)
    initial_count_res = client.get("/notifications/unread-count", headers=owner_headers)
    assert initial_count_res.status_code == 200
    initial_count = initial_count_res.json().get("unread_count", 0)

    # Trigger a new notification (Borrow Request)
    item_res = client.post("/items/", json={"name": "Projector"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post("/borrows/", json={"item_id": item_id}, headers=borrower_headers)

    # Get new count
    new_count_res = client.get("/notifications/unread-count", headers=owner_headers)
    new_count = new_count_res.json().get("unread_count", 0)

    # Count should increase exactly by 1
    assert new_count == initial_count + 1
