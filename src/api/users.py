from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.auth import get_current_active_user, get_current_admin_user
from src.crud.user import delete_user, get_user, get_users, update_user
from src.models.user import User
from src.schemas.user import UserResponse, UserUpdate
from src.utils.dependencies import get_db

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get the current user."""
    return current_user


@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_admin_user)],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Get all users. Admin only."""
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get a specific user."""
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Only allow users to see themselves, unless they're an admin
    if db_user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return db_user


@router.put("/{user_id}", response_model=UserResponse)
def update_user_api(
    user_id: int,
    user_in: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Update a user."""
    # Only allow users to update themselves, unless they're an admin
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user = update_user(db, user_id=user_id, user=user_in)
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_api(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Response:
    """Delete a user."""
    # Only allow users to delete themselves, unless they're an admin
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
