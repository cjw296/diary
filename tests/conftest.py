from functools import partial
from typing import Iterator, Iterable

import pytest

from models.user import User, UserCreate
from pytest_alembic import MigrationContext, create_alembic_fixture, runner, Config
from sqlalchemy import Engine, create_engine, Connection
from starlette.testclient import TestClient
from testservices.services.databases import PostgresContainer

from api import app
from api.deps import get_session
from sqlmodel import Session
from .helpers import get_superuser_token_headers, SUPERUSER_USERNAME, SUPERUSER_PASSWORD


@pytest.fixture(scope="session")
def client() -> Iterable[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='session')
def alembic_engine() -> Iterable[Engine]:
    with PostgresContainer() as database:
        yield create_engine(database.url)


@pytest.fixture(scope='session')
def engine_with_schema(alembic_engine: Engine) -> Iterable[Engine]:
    with runner(Config(), alembic_engine) as alembic_runner:
        alembic_runner.migrate_up_to("head")
        yield alembic_engine


@pytest.fixture()
def connection_in_transaction(engine_with_schema: Engine) -> Iterable[Connection]:
    with runner(Config(), engine_with_schema) as alembic_runner:
        connection = engine_with_schema.connect()
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture()
def session(connection_in_transaction: Connection) -> Iterator[Session]:
    with Session(connection_in_transaction, join_transaction_mode="create_savepoint") as session:
        app.dependency_overrides[get_session] = lambda: session
        try:
            yield session
        finally:
            app.dependency_overrides = {}


@pytest.fixture()
def superuser(session: Session) -> User:
    return User.create(
        session,
        UserCreate(
            email=SUPERUSER_USERNAME,
            password=SUPERUSER_PASSWORD,
            is_superuser=True,
        ),
    )


@pytest.fixture()
def superuser_token_headers(client: TestClient, superuser: User) -> dict[str, str]:
    return get_superuser_token_headers(client, superuser.email, SUPERUSER_PASSWORD)
