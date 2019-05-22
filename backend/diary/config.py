import os
from importlib import import_module
from pathlib import Path
from typing import List

from configurator import Config
from pydantic import BaseModel, PydanticValueError, urlstr
from pydantic.validators import str_validator


class ImportValueError(PydanticValueError):
    code = 'import'
    msg_template = 'Could not import {path}: {message}'


class Import(str):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        module_name, obj_name = v.split(':')
        try:
            module =  import_module(module_name)
            return getattr(module, obj_name)
        except (ImportError, AttributeError) as e:
            raise ImportValueError(message=str(e), path=v)


class DatabaseConfig(BaseModel):
    url: urlstr(schemes={'postgresql'}) = ...


class AppConfig(BaseModel):
    db: DatabaseConfig = ...
    middleware: List[Import] = []


def load_config():
    # defaults
    config = Config({
        'middleware': ['diary.api:make_session'],
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
