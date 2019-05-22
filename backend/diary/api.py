from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from starlette.requests import Request

from .config import load_config
from .model import Session, Event


app = FastAPI()


@app.on_event("startup")
def configure():
    config = load_config()
    Session.configure(bind=create_engine(config.db.url))
    for middleware in config.middleware:
        app.middleware('http')(middleware)


async def make_session(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response


def get_session(request: Request):
    return request.state.db


@app.get("/")
def root(session: Session = Depends(get_session)):
    return {"count": session.query(Event).count()}
