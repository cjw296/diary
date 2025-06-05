import secrets
from pathlib import Path

from configurator import Config

from zope import Client

SECRET_KEY: str = secrets.token_urlsafe(32)
# 60 minutes * 24 hours * 8 days = 8 days
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8


def read_config(path: str = 'config.yaml') -> Config:
    config = Config.from_path(path)
    config.diary_path = Path(config.diary_path).expanduser()
    if config.get('zope'):
        config.zope = Client(**config.zope.data)
    return config
