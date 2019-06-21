import os
from datetime import date

import pytest
from diary.api import app
from diary.config import config
from diary.model import Session, Base, Event, Types
from sqlalchemy.orm import configure_mappers
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


def test_list_empty(session, client):
    response = client.get("/events")
    compare(response.status_code, expected=200)
    compare(response.json(), expected={
        'items': [],
        'count': 0,
    })


def test_list_entries(session, client):
    session.add_all((
        Event(id=1, type=Types.event, text='test', date=date(2019, 1, 1)),
        Event(id=2, type=Types.done, text='something', date=date(2019, 1, 2)),
    ))
    session.flush()
    response = client.get("/events")
    compare(response.status_code, expected=200)
    compare(response.json(), expected={
        'items': [
            {'date': '2019-01-02', 'id': 2, 'text': 'something', 'type': 'DONE'},
            {'date': '2019-01-01', 'id': 1, 'text': 'test', 'type': 'EVENT'},
        ],
        'count': 2,
    })


def test_order_by_date_then_id(session, client):
    session.add_all((
        Event(id=1, text='three', date=date(2019, 1, 1)),
        Event(id=2, text='four', date=date(2019, 1, 1)),
        Event(id=3, text='one', date=date(2019, 1, 2)),
        Event(id=4, text='two', date=date(2019, 1, 2)),
    ))
    session.flush()
    response = client.get("/events")
    compare(response.status_code, expected=200)
    compare(response.json(), expected={
        'items': [
            {'date': '2019-01-02', 'id': 3, 'text': 'one', 'type': 'EVENT'},
            {'date': '2019-01-02', 'id': 4, 'text': 'two', 'type': 'EVENT'},
            {'date': '2019-01-01', 'id': 1, 'text': 'three', 'type': 'EVENT'},
            {'date': '2019-01-01', 'id': 2, 'text': 'four', 'type': 'EVENT'},
        ],
        'count': 4,
    })


def test_filter(session, client):
    session.add_all((
        Event(id=1, text='FISHES', date=date(2019, 1, 1)),
        Event(id=2, text='fish', date=date(2019, 1, 1)),
        Event(id=3, text='dogs', date=date(2019, 1, 2)),
        Event(id=4, text='cats', date=date(2019, 1, 2)),
    ))
    session.commit()
    response = client.get("/events?text=fish")
    compare(response.status_code, expected=200)
    compare(response.json(), expected={
        'items': [
            {'date': '2019-01-01', 'id': 1, 'text': 'FISHES', 'type': 'EVENT'},
            {'date': '2019-01-01', 'id': 2, 'text': 'fish', 'type': 'EVENT'},
        ],
        'count': 2,
    })


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
