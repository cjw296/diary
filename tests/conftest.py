from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Iterable
from uuid import UUID

import pytest
from sqlalchemy import Engine, create_engine, Connection
from starlette.testclient import TestClient
from testservices.provider import Provider
from testservices.services.databases import PostgresContainer, Database, DatabaseFromEnvironment

from api import app
from api.deps import get_session
from models.user import User, UserCreate
from pytest_alembic import runner, Config
from sqlmodel import Session
from .helpers import (
    get_user_token_headers,
    SUPERUSER_USERNAME,
    SUPERUSER_PASSWORD,
    NORMAL_USERNAME,
    NORMAL_PASSWORD,
)


@pytest.fixture(scope="session")
def client() -> Iterable[TestClient]:
    with TestClient(app) as c:
        yield c


database_provider = Provider[Database](
    DatabaseFromEnvironment(timeout=300),
    PostgresContainer(),
)


@pytest.fixture(scope='session')
def alembic_engine() -> Iterable[Engine]:
    with database_provider as database:
        yield create_engine(database.url)


@contextmanager
def override_get_session(session: Session) -> Iterator[None]:
    app.dependency_overrides[get_session] = lambda: session
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_session)


type Headers = dict[str, str]


@dataclass
class SessionFixtures:
    engine: Engine
    superuser: User
    superuser_headers: Headers
    normal_user: User
    normal_headers: Headers


@pytest.fixture(scope='session')
def session_fixtures(client: TestClient, alembic_engine: Engine) -> Iterable[SessionFixtures]:
    with runner(Config(), alembic_engine) as alembic_runner:
        alembic_runner.migrate_up_to("head")
        with Session(alembic_engine) as session, override_get_session(session):
            superuser = User.create(
                session,
                UserCreate(
                    email=SUPERUSER_USERNAME,
                    password=SUPERUSER_PASSWORD,
                    is_superuser=True,
                ),
            )
            normal_user = User.create(
                session,
                UserCreate(
                    email=NORMAL_USERNAME,
                    password=NORMAL_PASSWORD,
                    is_superuser=False,
                ),
            )
            session.commit()
            session.refresh(superuser)
            superuser_headers = get_user_token_headers(client, superuser.email, SUPERUSER_PASSWORD)
            normal_user_headers = get_user_token_headers(client, normal_user.email, NORMAL_PASSWORD)

        yield SessionFixtures(
            engine=alembic_engine,
            superuser=superuser,
            superuser_headers=superuser_headers,
            normal_user=normal_user,
            normal_headers=normal_user_headers,
        )


@pytest.fixture(scope='session')
def superuser_id(session_fixtures: SessionFixtures) -> UUID:
    return session_fixtures.superuser.id


@pytest.fixture(scope='session')
def normal_user_id(session_fixtures: SessionFixtures) -> UUID:
    return session_fixtures.normal_user.id


@pytest.fixture()
def connection_in_transaction(session_fixtures: SessionFixtures) -> Iterable[Connection]:
    connection = session_fixtures.engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()


@pytest.fixture()
def session(connection_in_transaction: Connection) -> Iterator[Session]:
    with (
        Session(connection_in_transaction, join_transaction_mode="create_savepoint") as session,
        override_get_session(session),
    ):
        yield session


@pytest.fixture()
def superuser_headers(session_fixtures: SessionFixtures, session: Session) -> Headers:
    # session is here because https://github.com/pytest-dev/pytest/issues/378
    return session_fixtures.superuser_headers


@pytest.fixture()
def normal_user_headers(session_fixtures: SessionFixtures, session: Session) -> Headers:
    # session is here because https://github.com/pytest-dev/pytest/issues/378
    return session_fixtures.normal_headers
