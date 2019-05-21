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


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response

class SessionGetter:

    session = None

    def __call__(self, request: Request):
        if self.session is None:
            return request.state.db
        else:
            return self.session

get_session = SessionGetter()


@app.get("/")
def root(session: Session = Depends(get_session)):
    return {"count": session.query(Event).count()}
