from diary.model import Session
from sqlalchemy import create_engine

from .api import app
from .config import load_config

@app.on_event("startup")
def configure():
    config = load_config()
    Session.configure(bind=create_engine(config.db.url))
