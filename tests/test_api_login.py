from fastapi.testclient import TestClient
from models.user import User
from sqlmodel import Session
from .helpers import check_response, SUPERUSER_USERNAME, SUPERUSER_PASSWORD


def test_login_invalid_credentials(client: TestClient, session: Session) -> None:
    login_data = {"username": "nonexistent@example.com", "password": "wrongpassword"}
    r = client.post("/login/access-token", data=login_data)
    check_response(r, {"detail": "Incorrect email or password"}, status_code=400)


def test_login_wrong_password(client: TestClient, session: Session) -> None:
    login_data = {"username": SUPERUSER_USERNAME, "password": "wrongpassword"}
    r = client.post("/login/access-token", data=login_data)
    check_response(r, {"detail": "Incorrect email or password"}, status_code=400)


def test_login_inactive_user(client: TestClient, session: Session) -> None:
    # Create an inactive user
    inactive_user = User(
        email="inactive@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        is_active=False,
    )
    session.add(inactive_user)
    session.commit()

    login_data = {"username": "inactive@example.com", "password": "secret"}
    r = client.post("/login/access-token", data=login_data)
    check_response(r, {"detail": "Inactive user"}, status_code=400)


def test_login_success(client: TestClient, session: Session) -> None:
    login_data = {"username": SUPERUSER_USERNAME, "password": SUPERUSER_PASSWORD}
    r = client.post("/login/access-token", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["access_token"]
