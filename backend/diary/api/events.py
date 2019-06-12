from datetime import date as DateType
from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.exc import NoResultFound

from .db import db_session
from diary.model import Session, Types, Event
from fastapi import APIRouter, Depends, Path, HTTPException
from pydantic import BaseModel, Required

router = APIRouter()


class EventNonPrimaryKey(BaseModel):
    date: DateType = ...
    type: Types = ...
    text: str = ...


class EventFull(EventNonPrimaryKey):
    id: int = ...


def simplify(obj):
    i = inspect(obj)
    return {attr: i.dict[attr] for attr in i.manager}


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


@router.delete("/{id}")
def delete_object(
    id: int,
    session: Session = Depends(db_session),
):
    """
    Delete an item.
    """
    with session.transaction:
        try:
            obj = session.query(Event).filter_by(id=id).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Event not found")
        else:
            session.delete(obj)
            return simplify(obj)
