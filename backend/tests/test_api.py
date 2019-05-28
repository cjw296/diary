import os

import pytest
from diary.api import app
from diary.model import Session, Base, Event, Done
from sqlalchemy import create_engine
from starlette.testclient import TestClient


@pytest.fixture(scope='session')
def client():
    os.environ['DB_URL'] = os.environ['TEST_DB_URL']
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope='session')
def db(client):
    engine = create_engine(os.environ['TEST_DB_URL'])
    conn = engine.connect()
    transaction = conn.begin()
    try:
        Session.configure(bind=conn)
        session = Session()
        Base.metadata.create_all(bind=conn, checkfirst=False)
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


def test_root_empty(session, client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 0}


def test_root_entries(session, client):
    session.add_all((
        Event(text='test'),
        Done(text='something'),
    ))
    session.flush()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 2}
