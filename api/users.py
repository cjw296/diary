import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from models.generic import Message
from models.security import verify_password, get_password_hash
from models.user import (
    UserPublic,
    UsersPublic,
    UserCreate,
    UserUpdateMe,
    UserUpdate,
    UpdatePassword,
)
from .deps import SessionDep, CurrentUser, get_current_active_superuser
from .crud import crud_user

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> UsersPublic:
    """Retrieve users."""

    users = crud_user.get_multi(session, skip=skip, limit=limit)
    return UsersPublic(data=users, count=crud_user.count(session))


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """Create new user using FastCRUD."""
    existing = crud_user.get_by(session, email=user_in.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    data = user_in.model_dump(exclude={"password"})
    data["hashed_password"] = get_password_hash(user_in.password)
    user = crud_user.create(session, obj_in=data)
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(*, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud_user.get_by(session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=409, detail="User with this email already exists")
    update_data = user_in.model_dump(exclude_unset=True)
    crud_user.update(session, db_obj=current_user, obj_in=update_data)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    crud_user.update(session, db_obj=current_user, obj_in={"hashed_password": hashed_password})
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    crud_user.remove(session, id=current_user.id)
    return Message(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.get(session, id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = crud_user.get(session, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist",
        )
    if user_in.email:
        existing_user = crud_user.get_by(session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    update_data = user_in.model_dump(exclude_unset=True)
    crud_user.update(session, db_obj=db_user, obj_in=update_data)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID) -> Message:
    """
    Delete a user.
    """
    user = crud_user.get(session, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    crud_user.remove(session, id=user_id)
    return Message(message="User deleted successfully")
