from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool

from ..config import config, load_config
from .db import db_session
from ..model import Session, Event
from . import events

app = FastAPI()


@app.on_event("startup")
def configure():
    load_config()
    Session.configure(bind=create_engine(config.db.url))


@app.middleware('http')
def make_db_session(request: Request, call_next):
    request.state.db = session = Session()
    with session.transaction:
        response = call_next(request)
    session.close()
    return response


@app.get("/")
def root(session: Session = Depends(db_session)):
    return {"count": session.query(Event).count()}


app.include_router(events.router, prefix="/events", tags=["events"])
