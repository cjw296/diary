import os
from contextlib import contextmanager

import pytest
from diary.model import Session, Base, Event, Done
from sqlalchemy import create_engine
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.testclient import TestClient
from diary.api import app, db_session_middleware

client = TestClient(app)


@contextmanager
def replace_middleware_dispatch(app, existing, replacement):
    app = app.error_middleware
    while True:
        app = getattr(app, 'app', None)
        if app is None:
            break
        if isinstance(app, BaseHTTPMiddleware) and app.dispatch_func is existing:
            app.dispatch_func = replacement
    yield
    # This should put things back like they were ;-)


@pytest.fixture(scope='session', autouse=True)
def db():
    engine = create_engine(os.environ['TEST_DB_URL'])
    conn = engine.connect()
    transaction = conn.begin()
    try:
        session = Session(bind=conn)
        Base.metadata.create_all(bind=conn, checkfirst=False)

        async def testing_session(request: Request, call_next):
            request.state.db = session
            return await call_next(request)

        with replace_middleware_dispatch(
            app, db_session_middleware, testing_session
        ):
            yield session
    finally:
        transaction.rollback()


@pytest.fixture()
def session(db):
    transaction = db.begin_nested()
    try:
            yield db
    finally:
        transaction.rollback()


def test_root_empty(session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 0}


def test_root_entries(session):
    session.add_all((
        Event(text='test'),
        Done(text='something'),
    ))
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 2}
