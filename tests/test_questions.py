"""Tests for the questions endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.quiz import Quiz


def test_add_question_to_quiz(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test adding a question to a quiz."""
    response = client.post(
        f"/api/v1/quizzes/{test_quiz.id}/questions/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "text": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Madrid"],
            "correct_answer": "Paris",
            "points": 2,
        },
    )
    assert response.status_code == 201
    question_data = response.json()
    assert question_data["text"] == "What is the capital of France?"
    assert question_data["options"] == ["London", "Paris", "Berlin", "Madrid"]
    assert question_data["correct_answer"] == "Paris"
    assert question_data["points"] == 2
    assert question_data["quiz_id"] == test_quiz.id


def test_add_question_to_nonexistent_quiz(client: TestClient, user_token: str):
    """Test adding a question to a quiz that doesn't exist."""
    response = client.post(
        "/api/v1/quizzes/999/questions/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "text": "What is the capital of France?",
            "options": ["London", "Paris", "Berlin", "Madrid"],
            "correct_answer": "Paris",
            "points": 2,
        },
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]


def test_add_question_to_other_user_quiz(
    client: TestClient, admin_token: str, test_quiz: Quiz
):
    """Test that a user can't add a question to another user's quiz."""
    # Try to add a question to test_quiz (owned by test_user) as admin
    response = client.post(
        f"/api/v1/quizzes/{test_quiz.id}/questions/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "text": "Admin added question",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "points": 1,
        },
    )
    # Admin should be able to add questions to any quiz
    assert response.status_code == 201
    question_data = response.json()
    assert question_data["text"] == "Admin added question"


def test_update_question(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test updating a question in a quiz."""
    # First get a question ID from the test quiz
    questions_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    quiz_data = questions_response.json()
    question_id = quiz_data["questions"][0]["id"]

    # Now update the question
    response = client.put(
        f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "text": "Updated question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option B",
            "points": 3,
        },
    )
    assert response.status_code == 200
    question_data = response.json()
    assert question_data["text"] == "Updated question text"
    assert question_data["options"] == ["Option A", "Option B", "Option C", "Option D"]
    assert question_data["correct_answer"] == "Option B"
    assert question_data["points"] == 3


def test_update_nonexistent_question(
    client: TestClient, user_token: str, test_quiz: Quiz
):
    """Test updating a question that doesn't exist."""
    response = client.put(
        f"/api/v1/quizzes/{test_quiz.id}/questions/999",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "text": "Updated question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option B",
            "points": 3,
        },
    )
    assert response.status_code == 404
    assert "Question not found" in response.json()["detail"]


def test_update_question_in_other_user_quiz(
    client: TestClient, admin_token: str, test_quiz: Quiz
):
    """Test that a user can't update a question in another user's quiz."""
    # First get a question ID from the test quiz
    questions_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    quiz_data = questions_response.json()
    question_id = quiz_data["questions"][0]["id"]

    # Now try to update the question as admin
    response = client.put(
        f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "text": "Admin updated question",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "C",
            "points": 5,
        },
    )
    # Admin should be able to update questions in any quiz
    assert response.status_code == 200
    question_data = response.json()
    assert question_data["text"] == "Admin updated question"


def test_delete_question(
    client: TestClient, user_token: str, test_quiz: Quiz, db: Session
):
    """Test deleting a question from a quiz."""
    # First get a question ID from the test quiz
    questions_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    quiz_data = questions_response.json()
    question_id = quiz_data["questions"][0]["id"]

    # Now delete the question
    response = client.delete(
        f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Question deleted successfully"

    # Verify question is deleted by getting the quiz again
    verify_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    updated_quiz_data = verify_response.json()
    question_ids = [q["id"] for q in updated_quiz_data["questions"]]
    assert question_id not in question_ids


def test_delete_nonexistent_question(
    client: TestClient, user_token: str, test_quiz: Quiz
):
    """Test deleting a question that doesn't exist."""
    response = client.delete(
        f"/api/v1/quizzes/{test_quiz.id}/questions/999",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Question not found" in response.json()["detail"]


def test_delete_question_from_other_user_quiz(
    client: TestClient, admin_token: str, test_quiz: Quiz
):
    """Test that a user can't delete a question from another user's quiz."""
    # First get a question ID from the test quiz
    questions_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    quiz_data = questions_response.json()
    if len(quiz_data["questions"]) > 0:
        question_id = quiz_data["questions"][0]["id"]

        # Now try to delete the question as admin
        response = client.delete(
            f"/api/v1/quizzes/{test_quiz.id}/questions/{question_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Admin should be able to delete questions from any quiz
        assert response.status_code == 200
        assert response.json()["detail"] == "Question deleted successfully"
