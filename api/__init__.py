from api import users, login
from fastapi import FastAPI

app = FastAPI(title='diary')
app.include_router(login.router, tags=["login"])
app.include_router(users.router, prefix="/users", tags=["users"])
