def test_non_admin_cannot_access_admin_routes(client, auth_headers):
    admin_headers = auth_headers()  # first user, becomes admin
    normal_headers = auth_headers(email="normal@example.com", username="normal")

    assert client.get("/admin/stats", headers=admin_headers).status_code == 200
    assert client.get("/admin/stats", headers=normal_headers).status_code == 403


def test_admin_stats_reflect_data(client, auth_headers):
    headers = auth_headers()
    board_id = client.post("/boards", json={"title": "Board"}, headers=headers).json()["id"]
    board = client.get(f"/boards/{board_id}", headers=headers).json()
    list_id = board["lists"][0]["id"]
    client.post(f"/lists/{list_id}/cards", json={"title": "A", "priority": "high"}, headers=headers)
    client.post(f"/lists/{list_id}/cards", json={"title": "B", "priority": "high"}, headers=headers)

    stats = client.get("/admin/stats", headers=headers).json()
    assert stats["total_boards"] == 1
    assert stats["total_cards"] == 2
    assert stats["cards_by_priority"]["high"] == 2
