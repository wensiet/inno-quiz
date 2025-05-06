"""Tests for auth dependencies to improve coverage."""

import pytest
from fastapi import HTTPException, status
from fastapi.security import SecurityScopes
from jose import jwt

from src.auth.dependencies import authenticate_user, get_current_user
from src.auth.utils import ALGORITHM, SECRET_KEY, create_access_token
from src.crud.user import create_user
from src.schemas.user import UserCreate


def test_authenticate_user_invalid_password(db):
    """Test authenticating a user with an invalid password."""
    result = authenticate_user(db, "admin", "wrongpassword")
    assert result is None


def test_authenticate_user_nonexistent_user(db):
    """Test authenticating a non-existent user."""
    result = authenticate_user(db, "nonexistentuser", "password123")
    assert result is None


def test_token_validation_no_sub(db):
    """Test validation of a token without a subject."""
    # Create a token without the 'sub' claim
    payload = {"scopes": ["user"]}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Test with user scope required
    security_scopes = SecurityScopes(scopes=["user"])
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(security_scopes, token, db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in excinfo.value.detail


def test_token_validation_invalid_jwt(db):
    """Test validation of an invalid JWT."""
    # Test with user scope required
    security_scopes = SecurityScopes(scopes=["user"])
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(security_scopes, "invalid.token.format", db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in excinfo.value.detail


def test_token_invalid_username(db):
    """Test a token with a username that doesn't exist."""
    # Create a token for a user that doesn't exist
    access_token = create_access_token(
        data={"sub": "nonexistentuser123", "scopes": ["user"]},
    )

    # Test with user scope required
    security_scopes = SecurityScopes(scopes=["user"])
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(security_scopes, access_token, db)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in excinfo.value.detail


def test_scope_validation(db):
    """Test scope validation."""
    # Create a test user with just "user" scope
    user_data = UserCreate(
        username="scopeuser",
        email="scopeuser@example.com",
        password="password123",
    )
    create_user(db, user_data)

    # Create a token with only user scope
    access_token = create_access_token(
        data={"sub": "scopeuser", "scopes": ["user"]},
    )

    # Test with admin scope required
    security_scopes = SecurityScopes(scopes=["admin"])

    # We need separate try/except because the error happens in a scope check
    try:
        get_current_user(security_scopes, access_token, db)
    except HTTPException as exc:
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in exc.detail
