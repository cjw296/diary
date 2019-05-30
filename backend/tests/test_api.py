import os

import pytest
from diary.api import app
from diary.config import config
from diary.model import Session, Base, Event, Done
from starlette.testclient import TestClient


@pytest.fixture(scope='session')
def client():
    with config.push({
        'testing': True,
        'db': {'url': os.environ['TEST_DB_URL']}
    }):
        with TestClient(app) as client:
            yield client


@pytest.fixture(scope='session')
def db(client):
    engine = Session.kw['bind']
    conn = engine.connect()
    transaction = conn.begin()
    try:
        Session.configure(bind=conn)
        session = Session()
        Base.metadata.create_all(bind=conn, checkfirst=False)
        yield session
    finally:
        transaction.rollback()
        Session.configure(bind=engine)


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
