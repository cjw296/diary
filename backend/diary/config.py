import os
from pathlib import Path
from typing import List

from configurator import Config
from pydantic import BaseModel, PyObject, urlstr


class DatabaseConfig(BaseModel):
    url: urlstr(schemes={'postgresql'}) = ...


class AppConfig(BaseModel):
    db: DatabaseConfig = ...
    middleware: List[PyObject] = []


def load_config():
    # defaults
    config = Config({
        'middleware': ['diary.api.make_db_session'],
    })

    # file
    config.merge(
        Config.from_path(Path(__file__).resolve().parent.parent / 'app.yml')
    )

    # env
    config.merge(os.environ, {
        'DB_URL': 'db.url',
    })

    return AppConfig(**config.data)
