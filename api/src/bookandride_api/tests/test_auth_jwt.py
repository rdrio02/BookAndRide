import pytest
from fastapi.testclient import TestClient
from bookandride_api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_register_login_and_access_books(client):  # <--- note 'client' argument
    # register
    r = client.post("/register",
                    json={"email":"bob@example.com","password":"Secret123"})
    assert r.status_code in (200, 201)

    # login
    r = client.post("/login",
                    json={"email":"bob@example.com","password":"Secret123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    # access protected endpoint without token -> 401
    r = client.get("/books")
    assert r.status_code == 401

    # access with token -> 200
    r = client.get("/books", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
