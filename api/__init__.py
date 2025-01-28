import os
from contextlib import asynccontextmanager

from sqlalchemy import create_engine

from config import read_config
from fastapi.routing import APIRoute

from api import users, login
from api import deps
from fastapi import FastAPI


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Changes the names of various parts of the auto-generated client.
    """
    return f"{route.tags[0]}-{route.name}"


@asynccontextmanager
async def lifespan(_: FastAPI):
    # set up config and engine when we're not running tests:
    if 'PYTEST_CURRENT_TEST' not in os.environ:
        config = read_config()
        deps.engine = create_engine(config.db)
        yield
        deps.engine.dispose()
        deps.engine = None
    else:
        yield


app = FastAPI(
    title='diary', generate_unique_id_function=custom_generate_unique_id, lifespan=lifespan
)
app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
