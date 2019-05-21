import os
import sys

import pytest
from diary.model import Session, Base, Event, Done
from sqlalchemy import create_engine
from starlette.testclient import TestClient
from diary.api import app, get_db


client = TestClient(app)


@pytest.fixture(scope='session', autouse=True)
def db():

    # hack to see if this works:
    import gc
    ignore = sys._getframe().f_globals
    for o in gc.get_referrers(get_db):
        assert isinstance(o, dict)
        if o is ignore:
            continue
        for key, value in tuple(o.items()):
            if value is get_db:
                o[key] = lambda request: session

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
