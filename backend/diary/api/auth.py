from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token",
    scopes={
        'read:entry': 'Read and search Entry objects',
        'write:entry': 'Create, modify and delete Entry objects',
    }
)


class User(BaseModel):
    username: str


# def get_current_user(security_scopes: SecurityScopes):
#     print(security_scopes.scopes)
#     return User(username='foo')
#
#
# def get_current_user(security_scopes: SecurityScopes):
#     print(security_scopes.scopes)
#     return User(username='foo')


from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

security = HTTPBasic()

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return credentials.username
