def test_create_board_seeds_default_lists(client, auth_headers):
    headers = auth_headers()
    resp = client.post("/boards", json={"title": "My Board", "description": "desc"}, headers=headers)
    assert resp.status_code == 201
    board_id = resp.json()["id"]

    detail = client.get(f"/boards/{board_id}", headers=headers).json()
    assert [l["title"] for l in detail["lists"]] == ["To Do", "In Progress", "Done"]


def test_board_not_visible_to_other_users(client, auth_headers):
    owner_headers = auth_headers()
    board_id = client.post("/boards", json={"title": "Private"}, headers=owner_headers).json()["id"]

    other_headers = auth_headers(email="mallory@example.com", username="mallory")
    resp = client.get(f"/boards/{board_id}", headers=other_headers)
    assert resp.status_code == 403


def test_invite_member_grants_access(client, auth_headers):
    owner_headers = auth_headers()
    board_id = client.post("/boards", json={"title": "Shared"}, headers=owner_headers).json()["id"]

    member_headers = auth_headers(email="mallory@example.com", username="mallory")

    resp = client.post(
        f"/boards/{board_id}/members", json={"email": "mallory@example.com"}, headers=owner_headers
    )
    assert resp.status_code == 201

    resp = client.get(f"/boards/{board_id}", headers=member_headers)
    assert resp.status_code == 200


def test_only_owner_can_delete_board(client, auth_headers):
    owner_headers = auth_headers()
    board_id = client.post("/boards", json={"title": "Board"}, headers=owner_headers).json()["id"]
    member_headers = auth_headers(email="mallory@example.com", username="mallory")
    client.post(f"/boards/{board_id}/members", json={"email": "mallory@example.com"}, headers=owner_headers)

    resp = client.delete(f"/boards/{board_id}", headers=member_headers)
    assert resp.status_code == 403

    resp = client.delete(f"/boards/{board_id}", headers=owner_headers)
    assert resp.status_code == 204
