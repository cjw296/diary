import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from models.user import User, UserCreate
from sqlmodel import Session, select
from .helpers import check_response, SUPERUSER_USERNAME


def test_get_users_superuser_me(
    client: TestClient, superuser: User, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(f"/users/me", headers=superuser_token_headers)
    check_response(
        r,
        {
            "is_active": True,
            "is_superuser": True,
            "email": superuser.email,
            "full_name": None,
            "id": str(superuser.id),
        },
    )
