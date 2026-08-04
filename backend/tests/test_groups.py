def test_group_visibility_flow(client):
    reg_owner = client.post(
        "/users/",
        json={"username": "owner", "password": "password123", "display_name": "Owner User"}
    )
    assert reg_owner.status_code in [200, 201], f"Registration failed: {reg_owner.json()}"
    owner_id = reg_owner.json()["id"]

    reg_friend = client.post(
        "/users/",
        json={"username": "friend", "password": "password123", "display_name": "Friend User"}
    )
    assert reg_friend.status_code in [200, 201], f"Registration failed: {reg_friend.json()}"
    friend_id = reg_friend.json()["id"]

    reg_stranger = client.post(
        "/users/",
        json={"username": "stranger", "password": "password123", "display_name": "Stranger User"}
    )
    assert reg_stranger.status_code in [200, 201], f"Registration failed: {reg_stranger.json()}"

    owner_login = client.post("/auth/login", data={"username": "owner", "password": "password123"})
    assert owner_login.status_code == 200, f"Login failed: {owner_login.json()}"
    owner_token = owner_login.json()["access_token"]
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    friend_login = client.post("/auth/login", data={"username": "friend", "password": "password123"})
    assert friend_login.status_code == 200, f"Login failed: {friend_login.json()}"
    friend_token = friend_login.json()["access_token"]
    friend_headers = {"Authorization": f"Bearer {friend_token}"}

    stranger_login = client.post("/auth/login", data={"username": "stranger", "password": "password123"})
    assert stranger_login.status_code == 200, f"Login failed: {stranger_login.json()}"
    stranger_token = stranger_login.json()["access_token"]
    stranger_headers = {"Authorization": f"Bearer {stranger_token}"}

    item_res = client.post(
        "/items/",
        headers=owner_headers,
        json={"name": "Secret Item", "description": "Hidden", "category": "Private"}
    )
    assert item_res.status_code in [200, 201], f"Create item failed: {item_res.json()}"
    item_id = item_res.json()["id"]

    group_res = client.post(
        "/groups",
        headers=owner_headers,
        json={"name": "Close Friends"}
    )
    assert group_res.status_code in [200, 201], f"Create group failed: {group_res.json()}"
    group_id = group_res.json()["id"]

    client.post(
        f"/groups/{group_id}/users",
        headers=owner_headers,
        json={"user_id": friend_id}
    )

    client.post(
        f"/groups/{group_id}/items",
        headers=owner_headers,
        json={"item_id": item_id}
    )

    owner_check = client.get(f"/items/user/{owner_id}", headers=owner_headers)
    assert owner_check.status_code == 200, f"Owner check failed: {owner_check.json()}"
    assert len(owner_check.json()) == 1
    assert owner_check.json()[0]["id"] == item_id

    friend_check = client.get(f"/items/user/{owner_id}", headers=friend_headers)
    assert friend_check.status_code == 200, f"Friend check failed: {friend_check.json()}"
    assert len(friend_check.json()) == 1
    assert friend_check.json()[0]["id"] == item_id

    stranger_check = client.get(f"/items/user/{owner_id}", headers=stranger_headers)
    assert stranger_check.status_code == 200, f"Stranger check failed: {stranger_check.json()}"
    assert len(stranger_check.json()) == 0
