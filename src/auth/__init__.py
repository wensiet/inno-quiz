"""Authentication package."""

# This file intentionally left empty to mark the directory as a package

# Re-export common utilities
from src.auth.dependencies import (
    authenticate_user,
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
)
from src.auth.utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)

__all__ = [
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "authenticate_user",
    "create_access_token",
    "get_current_active_user",
    "get_current_admin_user",
    "get_current_user",
    "get_password_hash",
    "verify_password",
]
