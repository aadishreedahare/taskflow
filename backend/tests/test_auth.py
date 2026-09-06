def test_register_and_login(client):
    resp = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "supersecret"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "bob@example.com"
    assert body["user"]["is_admin"] is True  # first user becomes admin

    resp = client.post(
        "/auth/login", data={"username": "bob@example.com", "password": "supersecret"}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "username": "carol", "password": "correcthorse"},
    )
    resp = client.post("/auth/login", data={"username": "carol@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_duplicate_email_rejected(client):
    payload = {"email": "dave@example.com", "username": "dave", "password": "password123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    payload["username"] = "dave2"
    assert client.post("/auth/register", json=payload).status_code == 400


def test_me_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    headers = auth_headers()
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "alice@example.com"
