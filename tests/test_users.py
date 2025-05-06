"""Tests for the users endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.user import User


def test_get_current_user(client: TestClient, user_token: str):
    """Test getting the current user."""
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"
    assert "id" in user_data
    assert "is_active" in user_data
    assert "is_superuser" in user_data
    assert "hashed_password" not in user_data


def test_get_current_user_without_token(client: TestClient):
    """Test getting the current user without a token."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_user_by_id(client: TestClient, test_user: User, user_token: str):
    """Test getting a user by ID."""
    response = client.get(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"
    assert user_data["id"] == test_user.id


def test_get_nonexistent_user(client: TestClient, user_token: str):
    """Test getting a user that doesn't exist."""
    response = client.get(
        "/api/v1/users/999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_all_users_as_admin(
    client: TestClient, admin_token: str, test_user: User, test_admin: User
):
    """Test getting all users as an admin."""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2  # At least the test user and admin
    # Check that both our test users are in the list
    usernames = [user["username"] for user in users]
    assert "testuser" in usernames
    assert "admin" in usernames


def test_get_all_users_as_normal_user(client: TestClient, user_token: str):
    """Test that normal users can't get all users."""
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_update_own_user(client: TestClient, user_token: str, test_user: User):
    """Test updating the current user."""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "email": "updated@example.com",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "updated@example.com"
    assert user_data["username"] == "testuser"  # Unchanged


def test_update_other_user_as_normal_user(
    client: TestClient, user_token: str, test_admin: User
):
    """Test that a normal user can't update another user."""
    response = client.put(
        f"/api/v1/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "email": "hacked@example.com",
        },
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_update_user_as_admin(client: TestClient, admin_token: str, test_user: User):
    """Test that an admin can update any user."""
    response = client.put(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "admin-updated@example.com",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "admin-updated@example.com"
    assert user_data["username"] == "testuser"  # Unchanged


def test_delete_own_user(
    client: TestClient, user_token: str, test_user: User, db: Session
):
    """Test deleting the current user."""
    response = client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 204

    # Verify user is deleted from the database
    from src.crud.user import get_user

    deleted_user = get_user(db, test_user.id)
    assert deleted_user is None


def test_delete_other_user_as_normal_user(
    client: TestClient, user_token: str, test_admin: User
):
    """Test that a normal user can't delete another user."""
    response = client.delete(
        f"/api/v1/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_delete_user_as_admin(
    client: TestClient, admin_token: str, test_user: User, db: Session
):
    """Test that an admin can delete any user."""
    response = client.delete(
        f"/api/v1/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 204

    # Verify user is deleted from the database
    from src.crud.user import get_user

    deleted_user = get_user(db, test_user.id)
    assert deleted_user is None
