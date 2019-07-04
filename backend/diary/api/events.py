from datetime import date as DateType
from typing import List
from urllib.parse import urlencode

from diary.model import Session, Types, Event
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Required
from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound
from starlette.requests import Request

from .db import db_session

router = APIRouter()


class EventNonPrimaryKey(BaseModel):
    date: DateType
    type: Types
    text: str


class EventFull(EventNonPrimaryKey):
    id: int


class EventList(BaseModel):
    items: List[EventFull]
    count: int
    prev: str = None
    next: str = None


def simplify(obj):
    i = inspect(obj)
    return {attr: i.dict.get(attr) for attr in i.manager}


def url_for(request, name, limit, offset):
    return request.url_for(name)+'?'+urlencode({'limit': limit, 'offset': offset})


@router.get("/", response_model=EventList, name='events_list')
def list_object(
    text: str = None,
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(db_session),
    request: Request = Required
):
    """
    Retrieve Events.
    """
    with session.transaction:
        items = session.query(Event).order_by(Event.date.desc(), 'id')

        if text:
            items = items.filter(Event.text.ilike('%'+text.strip()+'%'))
        count = items.count()
        items = [EventFull(**simplify(i)) for i in items.offset(offset).limit(limit)]

        if len(items) != count:

            if offset:
                prev_offset = max(offset-limit, 0)
                prev = url_for(request, 'events_list', limit, prev_offset)
            else:
                prev = None

            next_offset = offset + limit
            if next_offset < count:
                next = url_for(request, 'events_list', limit, next_offset)
            else:
                next = None

        else:
            prev = next = None

        return EventList(count=count, items=items, prev=prev, next=next)


@router.post("/", response_model=EventFull, status_code=201)
def create_object(
    event: EventNonPrimaryKey = Required,
    session: Session = Depends(db_session),
):
    """
    Create new Event.
    """
    with session.transaction:
        obj = Event(**event.dict())
        session.add(obj)
        session.flush()
        return simplify(obj)


@router.put("/{id}", response_model=EventFull)
def update_object(
    id: int,
    event: EventNonPrimaryKey = Required,
    session: Session = Depends(db_session),
):
    """
    Update an Event.
    """
    with session.transaction:
        try:
            obj = session.query(Event).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Event not found")
        else:
            for key, value in event.dict().items():
                setattr(obj, key, value)
            return simplify(obj)


@router.get("/{id}", response_model=EventFull)
def get_object(
    id: int,
    session: Session = Depends(db_session),
):
    """
    Get Event by ID.
    """
    with session.transaction:
        try:
            obj = session.query(Event).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Event not found")
        else:
            return simplify(obj)


@router.delete("/{id}", response_model=EventFull)
def delete_object(
    id: int,
    session: Session = Depends(db_session),
):
    """
    Delete an Event.
    """
    with session.transaction:
        try:
            obj = session.query(Event).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Event not found")
        else:
            session.delete(obj)
            return simplify(obj)
