from fastapi.routing import APIRoute

from api import users, login
from fastapi import FastAPI


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Changes the names of various parts of the auto-generated client.
    """
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(title='diary', generate_unique_id_function=custom_generate_unique_id)
app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
