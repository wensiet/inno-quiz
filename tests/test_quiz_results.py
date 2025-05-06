"""Tests for the quiz results endpoints."""

from fastapi.testclient import TestClient

from src.models.quiz import Quiz
from src.models.user import User


def test_submit_quiz_result(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test submitting a quiz result."""
    # First, get the quiz to extract question IDs
    quiz_response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    quiz_data = quiz_response.json()

    # Prepare answers for submission
    answers = []
    for question in quiz_data["questions"]:
        # For testing, we'll use the correct answer for the first question and incorrect for others
        correct = question["correct_answer"] if len(answers) == 0 else "Wrong answer"
        answers.append(
            {
                "question_id": question["id"],
                "answer": correct,
            }
        )

    response = client.post(
        f"/api/v1/quizzes/{test_quiz.id}/results/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "answers": answers,
        },
    )

    assert response.status_code == 201
    result_data = response.json()
    assert result_data["quiz_id"] == test_quiz.id
    assert "score" in result_data
    assert "max_score" in result_data
    assert "correct_answers" in result_data
    # We should have at least one correct answer (the first one)
    assert result_data["correct_answers"] >= 1
    # Score should be positive
    assert result_data["score"] > 0


def test_submit_quiz_result_without_auth(client: TestClient, test_quiz: Quiz):
    """Test submitting a quiz result without authentication."""
    response = client.post(
        f"/api/v1/quizzes/{test_quiz.id}/results/",
        json={
            "answers": [],
        },
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_submit_result_nonexistent_quiz(client: TestClient, user_token: str):
    """Test submitting a result for a quiz that doesn't exist."""
    response = client.post(
        "/api/v1/quizzes/999/results/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "answers": [],
        },
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]


def test_get_quiz_results(
    client: TestClient, user_token: str, test_quiz: Quiz, test_user: User
):
    """Test getting quiz results for a specific quiz."""
    # First submit a result to ensure there's at least one
    test_submit_quiz_result(client, user_token, test_quiz)

    # Now fetch the results
    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/results/",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 1

    # Verify structure of result data
    result = results[0]
    assert "id" in result
    assert result["quiz_id"] == test_quiz.id
    assert result["user_id"] == test_user.id
    assert "score" in result
    assert "max_score" in result
    assert "correct_answers" in result
    assert "completed_at" in result


def test_get_results_nonexistent_quiz(client: TestClient, user_token: str):
    """Test getting results for a quiz that doesn't exist."""
    response = client.get(
        "/api/v1/quizzes/999/results/",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]


def test_get_my_quiz_results(client: TestClient, user_token: str, test_user: User):
    """Test getting all quiz results for the current user."""
    response = client.get(
        "/api/v1/quizzes/results/user",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

    # If there are results, verify they belong to the current user
    if len(results) > 0:
        assert all(result["user_id"] == test_user.id for result in results)


def test_get_quiz_leaderboard(client: TestClient, user_token: str, test_quiz: Quiz):
    """Test getting the leaderboard for a specific quiz."""
    # First submit a result to ensure there's at least one entry
    test_submit_quiz_result(client, user_token, test_quiz)

    response = client.get(
        f"/api/v1/quizzes/{test_quiz.id}/results/leaderboard",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    leaderboard = response.json()
    assert isinstance(leaderboard, dict)
    assert "quiz_id" in leaderboard
    assert "quiz_title" in leaderboard
    assert "entries" in leaderboard
    assert isinstance(leaderboard["entries"], list)
    assert len(leaderboard["entries"]) >= 1

    # Check the first entry
    entry = leaderboard["entries"][0]
    assert "username" in entry
    assert "score" in entry
    assert "max_score" in entry
    assert "percentage" in entry


def test_get_leaderboard_nonexistent_quiz(client: TestClient, user_token: str):
    """Test getting the leaderboard for a quiz that doesn't exist."""
    response = client.get(
        "/api/v1/quizzes/999/results/leaderboard",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 404
    assert "Quiz not found" in response.json()["detail"]
