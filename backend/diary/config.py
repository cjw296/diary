import os
from pathlib import Path

from configurator import Config
from pydantic import BaseModel, DSN


# schema
class DatabaseConfig(BaseModel):
    url: DSN = ...


class AppConfig(BaseModel):
    testing: bool = ...
    db: DatabaseConfig = ...


# defaults
config = Config({
    'testing': False,
})


def load_config(path=None):
    if config.testing:
        return

    # file
    if path is None:
        path = Path(__file__).resolve().parent.parent / 'app.yml'
    config.merge(
        Config.from_path(path)
    )

    # env
    config.merge(os.environ, {
        'DB_URL': 'db.url',
    })

    # validate
    AppConfig(**config.data)


