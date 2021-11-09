from pathlib import Path

from configurator import Config

from zope import Client


def read_config() -> Config:
    config = Config.from_path('config.yaml')
    config.diary_path = Path(config.diary_path).expanduser()
    config.zope = Client(**config.zope.data)
    return config
