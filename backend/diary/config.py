import os
from pathlib import Path

from configurator import Config
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    url: str = ...


class AppConfig(BaseModel):
    db: DatabaseConfig = ...


def load_config(path=None):
    if path is None:
        path = Path(__file__).resolve().parent.parent / 'app.yml'
    config = Config.from_path(path)
    config.merge(os.environ, {
        'DB_URL': 'db.url',
    })
    AppConfig(**config.data)
    return config
