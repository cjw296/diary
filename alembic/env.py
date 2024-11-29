import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

from config import read_config

config = context.config

if config.config_file_name is not None and not os.environ.get('PYTEST_CURRENT_TEST'):
    fileConfig(config.config_file_name)

from models.user import SQLModel


def run_migrations_online() -> None:
    connectable = context.config.attributes.get("connection", None)

    if connectable is None:
        connectable = create_engine(
            read_config().db,
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=SQLModel.metadata,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError
else:
    run_migrations_online()
