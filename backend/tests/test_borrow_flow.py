"""
Integration tests for the borrow lifecycle workflow.
Tests request creation, state transitions (accept, handover, return, reject, cancel),
dispute resolution, and edge cases like attempting to borrow self-owned items.
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
    # 1. Register users
    owner_res = client.post("/users/", json={"username": owner_username, "display_name": owner_name, "password": "password123"})
    assert owner_res.status_code in [200, 201], f"Owner creation failed: {owner_res.text}"
    owner_id = owner_res.json()["id"]

    borrower_res = client.post("/users/", json={"username": borrower_username, "display_name": borrower_name, "password": "password123"})
    assert borrower_res.status_code in [200, 201], f"Borrower creation failed: {borrower_res.text}"
    borrower_id = borrower_res.json()["id"]

    # 2. Login users
    owner_login = client.post("/auth/login", data={"username": owner_username, "password": "password123"})
    owner_headers = {"Authorization": f"Bearer {owner_login.json()['access_token']}"}

    borrower_login = client.post("/auth/login", data={"username": borrower_username, "password": "password123"})
    borrower_headers = {"Authorization": f"Bearer {borrower_login.json()['access_token']}"}

    # 3. Create group
    group_res = client.post("/groups", json={"name": f"Test Group {owner_username}"}, headers=owner_headers)
    assert group_res.status_code in [200, 201], f"Group creation failed: {group_res.text}"
    group_id = group_res.json()["id"]

    # 4. Add borrower to group (Updated endpoint to /users)
    member_res = client.post(f"/groups/{group_id}/users", json={"user_id": borrower_id}, headers=owner_headers)
    assert member_res.status_code in [200, 201], f"Adding user to group failed: {member_res.text}"

    return owner_headers, borrower_headers, group_id


def test_complete_borrow_lifecycle(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "alice", "Alice", "bob", "Bob"
    )

    # Create item
    item_response = client.post(
        "/items/",
        json={
            "name": "Drill Machine",
            "description": "Heavy duty drill",
            "category": "Tools",
        },
        headers=owner_headers,
    )
    assert item_response.status_code in [200, 201], f"Item creation failed: {item_response.text}"
    item_id = item_response.json()["id"]

    # Assign item to group
    assign_res = client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)
    assert assign_res.status_code in [200, 201], f"Assigning item to group failed: {assign_res.text}"

    request_response = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    assert request_response.status_code == 201, f"Borrow request failed (IDOR block?): {request_response.text}"
    borrow_id = request_response.json()["id"]

    # Accept request
    accept_response = client.post(f"/borrows/{borrow_id}/accept", headers=owner_headers)
    assert accept_response.status_code == 200
    assert accept_response.json()["status"] == "ACCEPTED"

    # Owner handover confirmation
    owner_handover = client.post(f"/borrows/{borrow_id}/handover", headers=owner_headers)
    assert owner_handover.status_code == 200
    assert owner_handover.json()["status"] == "HANDOVER_PENDING"

    # Borrower handover confirmation
    borrower_handover = client.post(f"/borrows/{borrow_id}/handover", headers=borrower_headers)
    assert borrower_handover.status_code == 200
    assert borrower_handover.json()["status"] == "BORROWED"

    # Borrower return confirmation
    borrower_return = client.post(f"/borrows/{borrow_id}/return", headers=borrower_headers)
    assert borrower_return.status_code == 200
    assert borrower_return.json()["status"] == "RETURN_PENDING"

    # Owner return confirmation
    owner_return = client.post(f"/borrows/{borrow_id}/return", headers=owner_headers)
    assert owner_return.status_code == 200
    assert owner_return.json()["status"] == "RETURNED"


def test_reject_borrow_request(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "user_owner_1", "Owner One", "user_borrower_1", "Borrower One"
    )

    item_res = client.post("/items/", json={"name": "Camera"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    borrow_id = borrow_res.json()["id"]

    reject_res = client.post(f"/borrows/{borrow_id}/reject", headers=owner_headers)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "REJECTED"


def test_cancel_borrow_request(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "user_owner_2", "Owner Two", "user_borrower_2", "Borrower Two"
    )

    item_res = client.post("/items/", json={"name": "Projector"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    borrow_id = borrow_res.json()["id"]

    cancel_res = client.post(f"/borrows/{borrow_id}/cancel", headers=borrower_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELED"


def test_dispute_and_resolve_flow(client):
    owner_headers, borrower_headers, group_id = setup_sharing_users(
        client, "user_owner_3", "Owner Three", "user_borrower_3", "Borrower Three"
    )

    item_res = client.post("/items/", json={"name": "Console"}, headers=owner_headers)
    item_id = item_res.json()["id"]
    client.post(f"/groups/{group_id}/items", json={"item_id": item_id}, headers=owner_headers)

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    borrow_id = borrow_res.json()["id"]

    client.post(f"/borrows/{borrow_id}/accept", headers=owner_headers)
    client.post(f"/borrows/{borrow_id}/handover", headers=owner_headers)
    client.post(f"/borrows/{borrow_id}/handover", headers=borrower_headers)

    dispute_res = client.post(f"/borrows/{borrow_id}/dispute", headers=borrower_headers)
    assert dispute_res.status_code == 200
    assert dispute_res.json()["status"] == "DISPUTED"

    resolve_res = client.post(
        f"/borrows/{borrow_id}/resolve-dispute",
        json={"target_status": "RETURNED"},
        headers=owner_headers,
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RETURNED"


def test_cannot_borrow_own_item(client):
    owner_headers = get_auth_header(client, "charlie", "Charlie")

    item_res = client.post("/items/", json={"name": "Bicycle"}, headers=owner_headers)
    item_id = item_res.json()["id"]

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=owner_headers,
    )
    assert borrow_res.status_code == 400
