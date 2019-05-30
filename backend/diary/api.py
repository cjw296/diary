from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from starlette.requests import Request

from .config import config, load_config
from .model import Session, Event


app = FastAPI()


@app.on_event("startup")
def configure():
    load_config()
    Session.configure(bind=create_engine(config.db.url))


@app.middleware('http')
async def make_db_session(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response


def db_session(request: Request):
    return request.state.db


@app.get("/")
def root(session: Session = Depends(db_session)):
    return {"count": session.query(Event).count()}
