import os
import sys
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Point the app at a throwaway SQLite file before importing it.
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db.name}"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp()
os.environ["SECRET_KEY"] = "test-secret"

from app.main import app  # noqa: E402
from app.database import Base, get_db  # noqa: E402

engine = create_engine(os.environ["DATABASE_URL"], connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    def _register(email="alice@example.com", username="alice", password="password123"):
        resp = client.post(
            "/auth/register", json={"email": email, "username": username, "password": password}
        )
        assert resp.status_code == 201, resp.text
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _register
