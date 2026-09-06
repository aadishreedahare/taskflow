def _make_board_with_list(client, headers):
    board_id = client.post("/boards", json={"title": "Board"}, headers=headers).json()["id"]
    board = client.get(f"/boards/{board_id}", headers=headers).json()
    list_id = board["lists"][0]["id"]
    return board_id, list_id


def test_create_and_move_card(client, auth_headers):
    headers = auth_headers()
    board_id, list_id = _make_board_with_list(client, headers)

    resp = client.post(f"/lists/{list_id}/cards", json={"title": "Write tests"}, headers=headers)
    assert resp.status_code == 201
    card = resp.json()
    assert card["priority"] == "medium"

    board = client.get(f"/boards/{board_id}", headers=headers).json()
    second_list_id = board["lists"][1]["id"]

    resp = client.patch(f"/cards/{card['id']}", json={"list_id": second_list_id}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["list_id"] == second_list_id


def test_labels_and_comments_on_card(client, auth_headers):
    headers = auth_headers()
    board_id, list_id = _make_board_with_list(client, headers)
    card_id = client.post(f"/lists/{list_id}/cards", json={"title": "Task"}, headers=headers).json()["id"]

    label = client.post(
        f"/boards/{board_id}/labels", json={"name": "urgent", "color": "#ef4444"}, headers=headers
    ).json()

    resp = client.post(f"/cards/{card_id}/labels/{label['id']}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()["labels"]) == 1

    resp = client.post(f"/cards/{card_id}/comments", json={"content": "Looks good"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["content"] == "Looks good"

    comments = client.get(f"/cards/{card_id}/comments", headers=headers).json()
    assert len(comments) == 1


def test_search_cards_by_text(client, auth_headers):
    headers = auth_headers()
    _, list_id = _make_board_with_list(client, headers)
    client.post(f"/lists/{list_id}/cards", json={"title": "Fix login bug"}, headers=headers)
    client.post(f"/lists/{list_id}/cards", json={"title": "Buy groceries"}, headers=headers)

    resp = client.get("/search/cards", params={"q": "login"}, headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Fix login bug"


def test_delete_card(client, auth_headers):
    headers = auth_headers()
    _, list_id = _make_board_with_list(client, headers)
    card_id = client.post(f"/lists/{list_id}/cards", json={"title": "Temp"}, headers=headers).json()["id"]

    resp = client.delete(f"/cards/{card_id}", headers=headers)
    assert resp.status_code == 204
    assert client.get(f"/cards/{card_id}", headers=headers).status_code == 404
