from pathlib import Path
import tempfile
import os

from testfixtures import compare, TempDirectory

from diary.config import read_config


def test_read_config_basic():
    with TempDirectory() as td:
        config_content = """
diary_path: ~/diary
"""
        config_path = td.write('config.yaml', config_content)
        config = read_config(config_path)

        expected_path = Path("~/diary").expanduser()
        compare(config.diary_path, expected=expected_path)


def test_read_config_with_zope():
    with TempDirectory() as td:
        config_content = """
diary_path: ~/diary
zope:
  url: http://example.com
  username: testuser
  password: testpass
"""
        config_path = td.write('config.yaml', config_content)
        config = read_config(config_path)

        expected_path = Path("~/diary").expanduser()
        compare(config.diary_path, expected=expected_path)
        assert hasattr(config, 'zope')
        compare(config.zope.url, expected="http://example.com")


def test_read_config_without_zope():
    with TempDirectory() as td:
        config_content = """
diary_path: ~/diary
"""
        config_path = td.write('config.yaml', config_content)
        config = read_config(config_path)

        expected_path = Path("~/diary").expanduser()
        compare(config.diary_path, expected=expected_path)
        assert config.get('zope') is None
