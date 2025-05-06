"""Authentication dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.auth.utils import ALGORITHM, SECRET_KEY, verify_password
from src.schemas.user import TokenData, UserInDB
from src.utils.dependencies import get_db

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "admin": "Full access to all resources",
        "user": "Access to your resources",
    },
)


# Forward declaration to avoid circular imports
def get_db_user(db: Session, username: str) -> UserInDB | None:
    # Import the user module
    import src.crud.user as u
    # Return the user by username
    return u.get_user_by_username(db, username)


def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> UserInDB | None:
    """Authenticate a user."""
    user = get_db_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> UserInDB:
    """Get the current user from a JWT token."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = get_db_user(db, token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


def get_current_active_user(
    current_user: Annotated[
        UserInDB, Security(get_current_user, scopes=["user"])
    ],
) -> UserInDB:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: Annotated[
        UserInDB, Security(get_current_user, scopes=["admin"])
    ],
) -> UserInDB:
    """Get the current admin user."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
