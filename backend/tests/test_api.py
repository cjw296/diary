import os

import pytest
from diary.model import Session, Base, Event, Done
from sqlalchemy import create_engine
from starlette.testclient import TestClient
from diary.api import app, get_session

client = TestClient(app)


@pytest.fixture(scope='session', autouse=True)
def db():
    engine = create_engine(os.environ['TEST_DB_URL'])
    conn = engine.connect()
    transaction = conn.begin()
    try:
        session = Session(bind=conn)
        Base.metadata.create_all(bind=conn, checkfirst=False)
        yield session
    finally:
        transaction.rollback()


@pytest.fixture()
def session(db):
    transaction = db.begin_nested()
    try:
        get_session.session = db
        yield db
    finally:
        get_session.session = None
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
