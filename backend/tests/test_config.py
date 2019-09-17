from pathlib import Path
from unittest.mock import patch

import pytest
from diary.config import load_config, config
from pydantic import ValidationError
from testfixtures import TempDirectory, compare, ShouldRaise

valid_config_source = """
db:
  url: postgresql://foo:bar@baz/bob
"""

valid_config_obj = dict(
    db={'url': 'postgresql://foo:bar@baz/bob'},
    testing=False,
)


@pytest.fixture(autouse=True)
def clean_config():
    with config.push({'testing': False}):
        yield


@pytest.fixture()
def tmpdir():
    with TempDirectory(encoding='ascii') as d:
        yield d


@patch('diary.config.Path')
def test_default_location(mock_path, tmpdir):
    __file__ = tmpdir.write('backend/diary/config.py', valid_config_source)
    tmpdir.write('backend/app.yml', valid_config_source)
    mock_path.return_value = Path(__file__)
    load_config()
    compare(config.data, expected=valid_config_obj)


def test_invalid_config(tmpdir):
    path = tmpdir.write('app.yml', '{"db": []}')
    with ShouldRaise(ValidationError) as s:
        load_config(path)
    compare(str(s.raised), expected=(
        '1 validation error for AppConfig\n'
        'db\n'
        '  value is not a valid dict (type=type_error.dict)'
    ))
