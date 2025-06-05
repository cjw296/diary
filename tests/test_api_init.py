import os
from unittest.mock import patch, MagicMock

import pytest
from fastapi import FastAPI
from testfixtures import TempDirectory

from api import lifespan


@pytest.mark.asyncio
async def test_lifespan_non_test_environment():
    """Test lifespan context manager in non-test environment"""

    with TempDirectory() as td:
        # Create a mock config file
        config_content = """
db: sqlite:///test.db
diary_path: ~/diary
"""
        config_path = td.write('config.yaml', config_content)

        # Mock the environment to simulate non-test
        with patch.dict(os.environ, {}, clear=True):  # Clear PYTEST_CURRENT_TEST
            with patch('api.read_config') as mock_read_config:
                with patch('api.create_engine') as mock_create_engine:
                    with patch('api.deps') as mock_deps:
                        # Setup mocks
                        mock_config = MagicMock()
                        mock_config.db = "sqlite:///test.db"
                        mock_read_config.return_value = mock_config

                        mock_engine = MagicMock()
                        mock_create_engine.return_value = mock_engine

                        app = FastAPI()

                        # Test the lifespan context manager
                        async with lifespan(app):
                            # Verify setup was called
                            mock_read_config.assert_called_once()
                            mock_create_engine.assert_called_once_with("sqlite:///test.db")
                            assert mock_deps.engine == mock_engine

                        # Verify cleanup was called
                        mock_engine.dispose.assert_called_once()
                        assert mock_deps.engine is None


@pytest.mark.asyncio
async def test_lifespan_test_environment():
    """Test lifespan context manager in test environment (current behavior)"""

    # This simulates the current test environment where PYTEST_CURRENT_TEST is set
    with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': 'test_something'}):
        with patch('api.read_config') as mock_read_config:
            with patch('api.create_engine') as mock_create_engine:
                app = FastAPI()

                # Test the lifespan context manager
                async with lifespan(app):
                    # In test environment, these should not be called
                    mock_read_config.assert_not_called()
                    mock_create_engine.assert_not_called()
