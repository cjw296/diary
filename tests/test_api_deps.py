import jwt
from uuid import uuid4

from fastapi import HTTPException
from testfixtures import ShouldRaise

from api.deps import get_session, get_current_user, engine
from config import SECRET_KEY
from models.user import User
from sqlmodel import Session
from .conftest import SessionFixtures


def test_get_session_engine_not_initialized() -> None:
    # Save current engine and set to None
    original_engine = engine
    from api import deps

    deps.engine = None

    try:
        with ShouldRaise(AssertionError("Engine not initialized")):
            next(get_session())
    finally:
        # Restore engine
        deps.engine = original_engine


def test_get_session_success(session_fixtures) -> None:
    # This test exercises the successful path of get_session
    from api import deps

    original_engine = deps.engine
    deps.engine = session_fixtures.engine

    try:
        # This should work without error
        session_gen = get_session()
        session = next(session_gen)
        assert session is not None
        # Close the session properly
        try:
            next(session_gen)
        except StopIteration:
            pass
    finally:
        deps.engine = original_engine


def test_get_current_user_invalid_token(session: Session) -> None:
    invalid_token = "invalid.token.here"

    with ShouldRaise(HTTPException) as exception:
        get_current_user(session, invalid_token)

    assert exception.raised.status_code == 403
    assert exception.raised.detail == "Could not validate credentials"


def test_get_current_user_validation_error(session: Session) -> None:
    # Create a token with payload that will fail pydantic validation
    malformed_payload = {"sub": "not-a-uuid", "exp": "not-a-timestamp"}
    malformed_token = jwt.encode(malformed_payload, SECRET_KEY, algorithm="HS256")

    with ShouldRaise(HTTPException) as exception:
        get_current_user(session, malformed_token)

    assert exception.raised.status_code == 403
    assert exception.raised.detail == "Could not validate credentials"


def test_get_current_user_malformed_token(session: Session) -> None:
    # Create a token with None sub which causes validation error
    malformed_payload = {"sub": None}
    malformed_token = jwt.encode(malformed_payload, SECRET_KEY, algorithm="HS256")

    with ShouldRaise(HTTPException) as exception:
        get_current_user(session, malformed_token)

    assert exception.raised.status_code == 403  # ValidationError due to None sub
    assert exception.raised.detail == "Could not validate credentials"


def test_get_current_user_user_not_found(session: Session) -> None:
    # Create a token for a non-existent user
    fake_user_id = str(uuid4())
    payload = {"sub": fake_user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    with ShouldRaise(HTTPException) as exception:
        get_current_user(session, token)

    assert exception.raised.status_code == 404
    assert exception.raised.detail == "User not found"


def test_get_current_user_inactive_user(session: Session) -> None:
    # Create an inactive user
    inactive_user = User(
        email="inactive@example.com", hashed_password="hashed_password", is_active=False
    )
    session.add(inactive_user)
    session.commit()
    session.refresh(inactive_user)

    # Create a token for the inactive user
    payload = {"sub": str(inactive_user.id)}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    with ShouldRaise(HTTPException) as exception:
        get_current_user(session, token)

    assert exception.raised.status_code == 400
    assert exception.raised.detail == "Inactive user"
