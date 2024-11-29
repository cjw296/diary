from __future__ import annotations
from typing import Annotated, Generator

import jwt
from jwt import InvalidTokenError
from pydantic import ValidationError
from starlette import status

from config import SECRET_KEY
from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends, HTTPException
from models.generic import TokenPayload
from models.user import User

from sqlmodel import Session

from models import security

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


SessionDep = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
