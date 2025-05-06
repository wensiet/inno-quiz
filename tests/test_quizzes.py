"""Tests for the quizzes endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.quiz import Quiz
from src.models.user import User


def test_create_quiz(client: TestClient, user_token: str):
    """Test creating a quiz."""
    response = client.post(
        "/api/v1/quizzes/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "title": "New Test Quiz",
            "description": "A quiz created in a test",
            "is_public": True,
            "questions": [
                {
                    "text": "What is 1+1?",
                    "options": ["1", "2", "3", "4"],
                    "correct_answer": "2",
                    "points": 1,
                },
            ],
        },
    )
    assert response.status_code == 201
    quiz_data = response.json()
    assert quiz_data["title"] == "New Test Quiz"
    assert quiz_data["description"] == "A quiz created in a test"
    assert quiz_data["is_public"] is True
    assert len(quiz_data["questions"]) == 1
    assert quiz_data["questions"][0]["text"] == "What is 1+1?"
    assert quiz_data["questions"][0]["options"] == ["1", "2", "3", "4"]
    assert quiz_data["questions"][0]["correct_answer"] == "2"
    assert quiz_data["questions"][0]["points"] == 1


def test_create_quiz_without_auth(client: TestClient):
    """Test creating a quiz without authentication."""
    response = client.post(
        "/api/v1/quizzes/",
        json={
            "title": "New Test Quiz",
            "description": "A quiz created in a test",
            "is_public": True,
            "questions": [],
        },
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_quizzes(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test getting all quizzes."""
    response = client.get(
        "/api/v1/quizzes/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    quizzes = response.json()
    assert len(quizzes) >= 1

    # Verify our test quiz is in the list
    quiz_ids = [quiz["id"] for quiz in quizzes]
    assert test_quiz.id in quiz_ids


def test_get_my_quizzes(
    client: TestClient, user_token: str, test_quiz: Quiz, test_user: User
):
    """Test getting the current user's quizzes."""
    response = client.get(
        "/api/v1/quizzes/?my_quizzes=true",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    quizzes = response.json()
    assert len(quizzes) >= 1

    # Verify all quizzes belong to the test user
    author_ids = [quiz["author_id"] for quiz in quizzes]
    assert all(author_id == test_user.id for author_id in author_ids)


def test_get_quiz_by_id(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test getting a quiz by ID."""
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    quiz_data = response.json()
    assert quiz_data["id"] == test_quiz.id
    assert quiz_data["title"] == test_quiz.title
    assert quiz_data["description"] == test_quiz.description
    assert len(quiz_data["questions"]) == 2  # As defined in the test_quiz fixture


def test_get_nonexistent_quiz(client: TestClient, user_token: str):
    """Test getting a quiz that doesn't exist."""
    response = client.get(
        "/api/v1/quizzes/999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]


def test_update_own_quiz(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test updating a quiz owned by the current user."""
    response = client.put(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "title": "Updated Quiz Title",
            "description": "Updated quiz description",
        },
    )
    assert response.status_code == 200
    quiz_data = response.json()
    assert quiz_data["title"] == "Updated Quiz Title"
    assert quiz_data["description"] == "Updated quiz description"
    assert quiz_data["is_public"] == test_quiz.is_public  # Unchanged


def test_update_other_user_quiz(client: TestClient, admin_token: str, test_quiz: Quiz):
    """Test that a user can't update another user's quiz."""
    # Create a quiz owned by the test user, then try to update it as admin
    response = client.put(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Admin Updated Title",
        },
    )
    # Admin should be able to update any quiz
    assert response.status_code == 200
    quiz_data = response.json()
    assert quiz_data["title"] == "Admin Updated Title"


def test_delete_own_quiz(
    client: TestClient, user_token: str, test_quiz: Quiz, db: Session
):
    """Test deleting a quiz owned by the current user."""
    response = client.delete(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Quiz deleted successfully"

    # Verify quiz is deleted from the database
    from src.crud.quiz import get_quiz

    deleted_quiz = get_quiz(db, test_quiz.id)
    assert deleted_quiz is None


def test_delete_other_user_quiz(client: TestClient, admin_token: str, test_quiz: Quiz):
    """Test that a user can't delete another user's quiz."""
    # Create a quiz owned by the test user, then try to delete it as admin
    response = client.delete(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Admin should be able to delete any quiz
    assert response.status_code == 200
    assert response.json()["detail"] == "Quiz deleted successfully"
