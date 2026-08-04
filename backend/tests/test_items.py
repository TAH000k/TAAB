import pytest


def test_soft_delete_item_flow(client):
    user_data = {
        "username": "item_owner_test",
        "display_name": "Item Owner",
        "password": "password123"
    }
    signup_res = client.post("/users/", json=user_data)
    assert signup_res.status_code == 200

    login_res = client.post(
        "/auth/login",
        data={"username": "item_owner_test", "password": "password123"}
    )
    assert login_res.status_code == 200, f"Login failed with: {login_res.json()}"

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/items/",
        json={"name": "Drill", "description": "Electric Drill", "category": "Tools"},
        headers=headers
    )
    assert create_res.status_code == 200
    item_id = create_res.json()["id"]

    delete_res = client.delete(f"/items/{item_id}", headers=headers)
    assert delete_res.status_code == 200
    assert delete_res.json()["message"] == "Item deleted successfully"

    get_item_res = client.get(f"/items/{item_id}", headers=headers)
    assert get_item_res.status_code == 404
