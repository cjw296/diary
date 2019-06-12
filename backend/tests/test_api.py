import os
from datetime import date

import pytest
from diary.api import app
from diary.config import config
from diary.model import Session, Base, Event, Done, Types
from starlette.testclient import TestClient
from testfixtures import compare


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
        Base.metadata.create_all(bind=conn, checkfirst=False)
        yield conn
    finally:
        transaction.rollback()
        Session.configure(bind=engine)


@pytest.fixture()
def session(db):
    transaction = db.begin_nested()
    try:
        Session.configure(bind=db)
        yield Session()
    finally:
        transaction.rollback()


def test_root_empty(session, client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 0}


def test_root_entries(session, client):
    session.add_all((
        Event(text='test', date=date(2019, 1, 1)),
        Done(text='something', date=date(2019, 1, 2)),
    ))
    session.flush()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'count': 2}


def test_create_no_data(session, client):
    response = client.post('/events/', data={})
    compare(session.query(Event).count(), expected=0)
    compare(response.json(), expected={
        'detail': [{'loc': ['body', 'event'],
                    'msg': 'field required',
                    'type': 'value_error.missing'}]
    })
    compare(response.status_code, expected=422)


def test_create_full_data(session, client):
    response = client.post('/events/', json={
        'date': '2019-06-02',
        'type': 'DONE',
        'text': 'some stuff got done'
    })
    actual = session.query(Event).one()
    compare(actual.date, expected=date(2019, 6, 2))
    compare(type(actual), expected=Done)
    compare(response.json(), expected={
        'id': actual.id,
        'date': '2019-06-02',
        'type': 'DONE',
        'text': 'some stuff got done'
    })
    compare(response.status_code, expected=201)


def test_update(session, client):
    session.add(
        Event(id=1, text='old', date=date(2019, 1, 1), type=Types.cancelled),
    )
    session.flush()
    response = client.put('/events/1', json={
        'date': '2019-06-02',
        'type': 'DONE',
        'text': 'some stuff got done'
    })
    compare(response.json(), expected={
        'id': 1,
        'date': '2019-06-02',
        'type': 'DONE',
        'text': 'some stuff got done'
    })
    compare(response.status_code, expected=200)
    actual = session.query(Event).one()
    compare(actual.date, expected=date(2019, 6, 2))
    compare(type(actual), expected=Done)


def test_update_not_there(session, client):
    response = client.put('/events/1', json={
        'date': '2019-06-02',
        'type': 'DONE',
        'text': 'some stuff got done'
    })
    compare(response.json(), expected={
        'detail': 'Event not found'
    })
    compare(response.status_code, expected=404)
    compare(session.query(Event).count(), expected=0)


def test_get(session, client):
    session.add(
        Event(id=1, text='current', date=date(2019, 1, 1), type=Types.cancelled),
    )
    session.flush()
    response = client.get('/events/1')
    compare(response.json(), expected={
        'id': 1,
        'date': '2019-01-01',
        'type': 'CANCELLED',
        'text': 'current'
    })
    compare(response.status_code, expected=200)


def test_get_not_there(session, client):
    response = client.get('/events/1')
    compare(response.json(), expected={
        'detail': 'Event not found'
    })
    compare(response.status_code, expected=404)


def test_delete(session, client):
    session.add(
        Event(id=1, text='old', date=date(2019, 1, 1), type=Types.cancelled),
    )
    session.flush()
    response = client.delete('/events/1')
    compare(response.json(), expected={
        'id': 1,
        'date': '2019-01-01',
        'type': 'CANCELLED',
        'text': 'old'
    })
    compare(response.status_code, expected=200)
    compare(session.query(Event).count(), expected=0)


def test_delete_not_there(session, client):
    session.add(
        Event(id=2, text='old', date=date(2019, 1, 1), type=Types.cancelled),
    )
    response = client.delete('/events/1')
    compare(response.json(), expected={
        'detail': 'Event not found'
    })
    compare(response.status_code, expected=404)
    compare(session.query(Event).count(), expected=1)
