"""Tests specifically for improving coverage of the questions endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.crud.quiz import get_quiz, update_quiz
from src.models.quiz import Quiz
from src.schemas.quiz import QuizUpdate


def test_get_questions_private_quiz(
    client: TestClient, user_token: str, test_quiz: Quiz, db: Session
):
    """Test accessing questions from a private quiz."""
    # First make the quiz private
    update_quiz(db, test_quiz.id, QuizUpdate(is_public=False))

    # Now try to get the questions as the owner
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/questions/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    # Owner should be able to access their private quiz questions
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_questions_private_quiz_other_user(
    client: TestClient, admin_token: str, test_quiz: Quiz, db: Session
):
    """Test accessing questions from another user's private quiz."""
    # First make the quiz private
    update_quiz(db, test_quiz.id, QuizUpdate(is_public=False))

    # Now try to get the questions as another user
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/questions/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Other users should not be able to access private quiz questions
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def test_get_questions_nonexistent_quiz(client: TestClient, user_token: str):
    """Test getting questions from a quiz that doesn't exist."""
    response = client.get(
        "/api/v1/quizzes/999/questions/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]


def test_get_specific_question(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test getting a specific question by ID."""
    # First get a question ID from the test quiz
    quiz_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    quiz_data = quiz_response.json()
    question_id = quiz_data["questions"][0]["id"]

    # Now get the specific question
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == question_id


def test_get_nonexistent_question(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test getting a question that doesn't exist."""
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/questions/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Question not found" in response.json()["detail"]


def test_get_private_quiz_question_other_user(
    client: TestClient, admin_token: str, test_quiz: Quiz, db: Session
):
    """Test accessing a specific question from another user's private quiz."""
    # First make the quiz private
    update_quiz(db, test_quiz.id, QuizUpdate(is_public=False))

    # Get a question ID
    quiz = get_quiz(db, test_quiz.id)
    question_id = quiz.questions[0].id

    # Now try to get the question as another user
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Other users should not be able to access private quiz questions
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]
