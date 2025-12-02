from pathlib import Path

from configurator import Config

from diary.zope import Client


def read_config(path: str = 'config.yaml') -> Config:
    config = Config.from_path(path)
    config.diary_path = Path(config.diary_path).expanduser()
    if config.get('zope'):
        config.zope = Client(**config.zope.data)
    return config
