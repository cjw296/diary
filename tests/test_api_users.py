from uuid import UUID, uuid4

from testfixtures import compare

from fastapi.testclient import TestClient
from models.security import verify_password
from models.user import User, UserCreate
from sqlmodel import Session, select
from .conftest import SessionFixtures, Headers
from .helpers import (
    check_response,
    SUPERUSER_USERNAME,
    random_lower_string,
    NORMAL_USERNAME,
    NORMAL_PASSWORD,
)


def test_use_access_token(
    client: TestClient, superuser_id: UUID, superuser_headers: Headers
) -> None:
    r = client.post("/login/test-token", headers=superuser_headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": True,
            "email": SUPERUSER_USERNAME,
            "full_name": None,
            "id": str(superuser_id),
        },
    )


def test_get_users_superuser_me(
    client: TestClient, superuser_id: UUID, superuser_headers: Headers
) -> None:
    r = client.get("/users/me", headers=superuser_headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": True,
            "email": SUPERUSER_USERNAME,
            "full_name": None,
            "id": str(superuser_id),
        },
    )


def test_get_users_normal_user_me(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID
) -> None:
    r = client.get("/users/me", headers=normal_user_headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": False,
            "email": NORMAL_USERNAME,
            "full_name": None,
            "id": str(normal_user_id),
        },
    )


def test_create_user_new_email(client: TestClient, superuser_headers, session: Session) -> None:
    username = 'new@example.com'
    r = client.post(
        "/users/",
        headers=superuser_headers,
        json={"email": username, "password": random_lower_string()},
    )
    user = User.by_email(session, email=r.json()["email"])
    assert user is not None
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": False,
            "email": username,
            "full_name": None,
            "id": str(user.id),
        },
    )


def test_get_existing_user(client: TestClient, superuser_headers, session: Session) -> None:
    username = 'existing@example.com'
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = User.create(session, user_in)
    user_id = user.id
    r = client.get(f"/users/{user_id}", headers=superuser_headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": False,
            "email": username,
            "full_name": None,
            "id": str(user.id),
        },
    )


def test_get_existing_user_current_user(client: TestClient, session: Session) -> None:
    username = 'existing@example.com'
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = User.create(session, user_in)
    user_id = user.id

    data = client.post(
        "/login/access-token",
        data={"username": username, "password": password},
    ).json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get(f"/users/{user_id}", headers=headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": False,
            "email": username,
            "full_name": None,
            "id": str(user.id),
        },
    )


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_headers: Headers
) -> None:
    r = client.get(f"/users/{uuid4()}", headers=normal_user_headers)
    check_response(r, {"detail": "The user doesn't have enough privileges"}, status_code=403)


def test_create_user_existing_username(
    client: TestClient, superuser_headers, session: Session
) -> None:
    username = 'existing@example.com'
    user_in = UserCreate(email=username, password=random_lower_string())
    User.create(session, user_in)
    r = client.post(
        "/users/",
        headers=superuser_headers,
        json={"email": username, "password": random_lower_string()},
    )
    check_response(
        r,
        {"detail": 'The user with this email already exists in the system.'},
        status_code=400,
    )


def test_create_user_by_normal_user(client: TestClient, normal_user_headers: Headers) -> None:
    r = client.post(
        "/users/",
        headers=normal_user_headers,
        json={"email": 'new@example.com', "password": random_lower_string()},
    )
    check_response(
        r,
        {"detail": "The user doesn't have enough privileges"},
        status_code=403,
    )


def test_retrieve_users(
    client: TestClient, session_fixtures: SessionFixtures, session: Session
) -> None:
    username1 = '1@example.com'
    user_in1 = UserCreate(email=username1, password=random_lower_string())
    user1 = User.create(session, user_in1)

    username2 = '2@example.com'
    user_in2 = UserCreate(email=username2, password=random_lower_string())
    user2 = User.create(session, user_in2)

    r = client.get("/users/", headers=session_fixtures.superuser_headers)
    check_response(
        r,
        {
            'count': 4,
            'data': [
                # alphabetically sorted
                {
                    'email': username1,
                    'full_name': None,
                    "id": str(user1.id),
                    'is_active': True,
                    'is_superuser': False,
                },
                {
                    'email': username2,
                    'full_name': None,
                    "id": str(user2.id),
                    'is_active': True,
                    'is_superuser': False,
                },
                {
                    'email': NORMAL_USERNAME,
                    'full_name': None,
                    "id": str(session_fixtures.normal_user.id),
                    'is_active': True,
                    'is_superuser': False,
                },
                {
                    'email': SUPERUSER_USERNAME,
                    'full_name': None,
                    "id": str(session_fixtures.superuser.id),
                    'is_active': True,
                    'is_superuser': True,
                },
            ],
        },
    )


def test_retrieve_users_by_normal_user(client: TestClient, normal_user_headers: Headers) -> None:
    r = client.get("/users/", headers=normal_user_headers)
    check_response(
        r,
        {"detail": "The user doesn't have enough privileges"},
        status_code=403,
    )


def test_update_user_me(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    r = client.patch(
        "/users/me",
        headers=normal_user_headers,
        json={"full_name": "Updated Name", "email": 'new@example.com'},
    )
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": False,
            "email": 'new@example.com',
            "full_name": "Updated Name",
            "id": str(normal_user_id),
        },
    )
    session.rollback()
    user = session.exec(select(User).filter_by(id=normal_user_id)).one()
    compare(
        user,
        expected=User(
            id=normal_user_id,
            full_name="Updated Name",
            username="new@example.com",
            email="new@example.com",
            hashed_password=user.hashed_password,
        ),
    )


def test_update_password_me(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    new_password = random_lower_string()
    assert new_password != NORMAL_PASSWORD
    r = client.patch(
        "/users/me/password",
        headers=normal_user_headers,
        json={"current_password": NORMAL_PASSWORD, "new_password": new_password},
    )
    check_response(r, {'message': 'Password updated successfully'})
    user = session.exec(select(User).filter_by(id=normal_user_id)).one()
    assert verify_password(new_password, user.hashed_password)


def test_update_password_me_incorrect_password(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    current_hash = session.exec(select(User.hashed_password).filter_by(id=normal_user_id)).one()
    new_password = random_lower_string()
    assert new_password != NORMAL_PASSWORD
    r = client.patch(
        "/users/me/password",
        headers=normal_user_headers,
        json={"current_password": new_password, "new_password": new_password},
    )
    check_response(r, {'detail': 'Incorrect password'}, status_code=400)
    new_hash = session.exec(select(User.hashed_password).filter_by(id=normal_user_id)).one()
    compare(expected=current_hash, actual=new_hash)


def test_update_user_me_email_exists(
    client: TestClient, normal_user_headers: Headers, session: Session
) -> None:
    username = 'another@example.com'
    password = random_lower_string()
    user = User.create(session, UserCreate(email=username, password=password))
    r = client.patch(
        "/users/me",
        headers=normal_user_headers,
        json={"email": user.email},
    )
    check_response(r, {'detail': "User with this email already exists"}, status_code=409)


def test_update_password_me_same_password_error(
    client: TestClient, normal_user_headers: Headers, session: Session
) -> None:
    r = client.patch(
        "/users/me/password",
        headers=normal_user_headers,
        json={"current_password": NORMAL_PASSWORD, "new_password": NORMAL_PASSWORD},
    )
    check_response(
        r, {'detail': "New password cannot be the same as the current one"}, status_code=400
    )


def test_update_user(
    client: TestClient, superuser_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    r = client.patch(
        f"/users/{normal_user_id}",
        headers=superuser_headers,
        json={"full_name": "New Name"},
    )
    check_response(
        r,
        {
            'id': str(normal_user_id),
            'email': 'testnormaluser@example.com',
            'full_name': 'New Name',
            'is_active': True,
            'is_superuser': False,
        },
    )
    session.rollback()
    user = session.exec(select(User).where(User.email == 'testnormaluser@example.com')).one()
    compare(user.full_name, expected='New Name')


def test_update_user_not_exists(
    client: TestClient, superuser_headers: Headers, session: Session
) -> None:
    r = client.patch(
        f"/users/{uuid4()}",
        headers=superuser_headers,
        json={"full_name": "Updated_full_name"},
    )
    check_response(r, {'detail': "The user with this id does not exist"}, status_code=404)


def test_update_user_email_exists(
    client: TestClient, superuser_headers: Headers, session: Session
) -> None:
    username1 = '1@example.com'
    user_in1 = UserCreate(email=username1, password=random_lower_string())
    user1 = User.create(session, user_in1)

    username2 = '2@example.com'
    user_in2 = UserCreate(email=username2, password=random_lower_string())
    user2 = User.create(session, user_in2)

    r = client.patch(
        f"/users/{user1.id}",
        headers=superuser_headers,
        json={"email": user2.email},
    )
    check_response(r, {'detail': "User with this email already exists"}, status_code=409)


def test_delete_user_me(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    r = client.delete(
        "/users/me",
        headers=normal_user_headers,
    )
    check_response(r, {'message': "User deleted successfully"})
    session.rollback()
    result = session.exec(select(User).where(User.id == normal_user_id)).first()
    assert result is None


def test_delete_user_me_as_superuser(
    client: TestClient,
    superuser_headers: Headers,
) -> None:
    r = client.delete(
        "/users/me",
        headers=superuser_headers,
    )
    check_response(
        r, {'detail': "Super users are not allowed to delete themselves"}, status_code=403
    )


def test_delete_user_super_user(
    client: TestClient, superuser_headers: Headers, normal_user_id: UUID, session: Session
) -> None:
    r = client.delete(
        f"/users/{normal_user_id}",
        headers=superuser_headers,
    )
    check_response(r, {'message': "User deleted successfully"})
    session.rollback()
    result = session.exec(select(User).where(User.id == normal_user_id)).first()
    assert result is None


def test_delete_user_not_found(client: TestClient, superuser_headers: Headers) -> None:
    r = client.delete(
        f"/users/{uuid4()}",
        headers=superuser_headers,
    )
    check_response(r, {'detail': "User not found"}, status_code=404)


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_headers: Headers, superuser_id: UUID, session: Session
) -> None:
    r = client.delete(
        f"/users/{superuser_id}",
        headers=superuser_headers,
    )
    check_response(
        r, {'detail': "Super users are not allowed to delete themselves"}, status_code=403
    )


def test_delete_user_without_privileges(
    client: TestClient, normal_user_headers: Headers, normal_user_id: UUID
) -> None:
    r = client.delete(
        f"/users/{normal_user_id}",
        headers=normal_user_headers,
    )
    check_response(r, {"detail": "The user doesn't have enough privileges"}, status_code=403)
