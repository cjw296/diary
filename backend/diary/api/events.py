from datetime import date as DateType
from typing import List

from .db import db_session
from diary.model import Session, Types, Event
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class EventCreate(BaseModel):
    date: DateType = ...
    type: Types = ...
    text: str = ...


class EventRead(EventCreate):
    id: int = ...


@router.post("/", response_model=EventRead, status_code=201)
def create_object(
    *,
    session: Session = Depends(db_session),
    event: EventCreate,
):
    """
    Create new Event.
    """
    event = Event(**event.dict())
    session.add(event)
    session.flush()
    return event


