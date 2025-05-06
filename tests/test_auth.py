"""Tests for the authentication endpoints."""

from fastapi.testclient import TestClient

from src.models.user import User


def test_login(client: TestClient, test_user: User):
    """Test the login endpoint."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123", "scope": "user"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, test_user: User):
    """Test login with incorrect password."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "wrongpassword", "scope": "user"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_incorrect_username(client: TestClient):
    """Test login with incorrect username."""
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "nonexistentuser",
            "password": "password123",
            "scope": "user",
        },
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_register(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["username"] == "newuser"
    assert user_data["email"] == "new@example.com"
    assert "id" in user_data
    assert "is_active" in user_data
    assert "is_superuser" in user_data
    assert "hashed_password" not in user_data


def test_register_existing_username(client: TestClient, test_user: User):
    """Test registration with existing username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",  # Already exists
            "email": "new@example.com",
            "password": "password123",
            "is_active": True,
        },
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_register_existing_email(client: TestClient, test_user: User):
    """Test registration with existing email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "test@example.com",  # Already exists
            "password": "password123",
            "is_active": True,
        },
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
