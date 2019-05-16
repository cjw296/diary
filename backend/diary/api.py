from fastapi import FastAPI, Depends
from starlette.requests import Request

from .model import Session, Event

app = FastAPI()

def get_db(request: Request):
    return request.state.db


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = Session()
    response = await call_next(request)
    request.state.db.close()
    return response


@app.get("/")
def root(session: Session = Depends(get_db)):
    return {"count": session.query(Event).count()}

