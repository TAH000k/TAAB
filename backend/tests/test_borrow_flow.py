"""
Integration tests for the borrow lifecycle workflow.
Tests request creation, state transitions (accept, handover, return, reject, cancel),
dispute resolution, and edge cases like attempting to borrow self-owned items.
"""

import pytest


def get_auth_header(client, username: str, display_name: str) -> dict:
    """
    Helper function to register a test user, log in, and return HTTP authorization headers.

    Args:
        client: FastAPI test client.
        username (str): Username for registration and auth.
        display_name (str): Display name for registration.

    Returns:
        dict: Headers dictionary containing the Bearer access token.
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


def test_complete_borrow_lifecycle(client):
    """
    Tests the full end-to-end happy path for a borrow transaction:
    Request -> Accept -> Owner Handover -> Borrower Handover (BORROWED) -> Borrower Return -> Owner Return (RETURNED).
    """
    owner_headers = get_auth_header(client, "alice", "Alice")
    borrower_headers = get_auth_header(client, "bob", "Bob")

    item_response = client.post(
        "/items/",
        json={
            "name": "Drill Machine",
            "description": "Heavy duty drill",
            "category": "Tools",
        },
        headers=owner_headers,
    )
    assert item_response.status_code == 200
    item_id = item_response.json()["id"]

    request_response = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    assert request_response.status_code == 201
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
    """
    Tests that an item owner can reject a pending borrow request.
    """
    owner_headers = get_auth_header(client, "user_owner_1", "Owner One")
    borrower_headers = get_auth_header(client, "user_borrower_1", "Borrower One")

    item_res = client.post(
        "/items/",
        json={"name": "Camera"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]

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
    """
    Tests that a borrower can cancel their pending borrow request.
    """
    owner_headers = get_auth_header(client, "user_owner_2", "Owner Two")
    borrower_headers = get_auth_header(client, "user_borrower_2", "Borrower Two")

    item_res = client.post(
        "/items/",
        json={"name": "Projector"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]

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
    """
    Tests raising a dispute on an active borrow and resolving it to a target status.
    """
    owner_headers = get_auth_header(client, "user_owner_3", "Owner Three")
    borrower_headers = get_auth_header(client, "user_borrower_3", "Borrower Three")

    item_res = client.post(
        "/items/",
        json={"name": "Console"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=borrower_headers,
    )
    borrow_id = borrow_res.json()["id"]

    client.post(f"/borrows/{borrow_id}/accept", headers=owner_headers)
    client.post(f"/borrows/{borrow_id}/handover", headers=owner_headers)
    client.post(f"/borrows/{borrow_id}/handover", headers=borrower_headers)

    # Raise dispute during active borrowing
    dispute_res = client.post(f"/borrows/{borrow_id}/dispute", headers=borrower_headers)
    assert dispute_res.status_code == 200
    assert dispute_res.json()["status"] == "DISPUTED"

    # Resolve dispute by owner
    resolve_res = client.post(
        f"/borrows/{borrow_id}/resolve-dispute",
        json={"target_status": "RETURNED"},
        headers=owner_headers,
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RETURNED"


def test_cannot_borrow_own_item(client):
    """
    Tests that a user cannot request to borrow an item that they own.
    """
    owner_headers = get_auth_header(client, "charlie", "Charlie")

    item_res = client.post(
        "/items/",
        json={"name": "Bicycle"},
        headers=owner_headers,
    )
    item_id = item_res.json()["id"]

    borrow_res = client.post(
        "/borrows/",
        json={"item_id": item_id},
        headers=owner_headers,
    )
    assert borrow_res.status_code == 400
