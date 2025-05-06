from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.utils import get_password_hash
from src.main import create_app
from src.models.base import Base
from src.models.user import User
from src.utils.dependencies import get_db

# Create a test database in memory
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Override the get_db dependency
def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the app with test settings
app = create_app()
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a test user
    db = TestingSessionLocal()
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db.add(test_user)
    db.commit()
    db.close()

    yield client

    # Drop tables
    Base.metadata.drop_all(bind=engine)


def get_token(test_client: TestClient) -> str:
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123", "scope": "user"},
    )
    return response.json()["access_token"]


def test_read_main(test_client: TestClient) -> None:
    response = test_client.get("/")
    assert response.status_code == 200
    assert "app" in response.json()
    assert "version" in response.json()


def test_auth_token(test_client: TestClient) -> None:
    response = test_client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "password123", "scope": "user"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "token_type" in token_data
    assert token_data["token_type"] == "bearer"


def test_get_users_me(test_client: TestClient) -> None:
    token = get_token(test_client)
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"


def test_create_quiz(test_client: TestClient) -> None:
    token = get_token(test_client)
    quiz_data = {
        "title": "Test Quiz",
        "description": "This is a test quiz",
        "questions": [
            {
                "text": "What is 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "points": 1,
            },
        ],
    }

    response = test_client.post(
        "/api/v1/quizzes/",
        headers={"Authorization": f"Bearer {token}"},
        json=quiz_data,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Quiz"
    assert data["description"] == "This is a test quiz"
    assert len(data["questions"]) == 1
    assert data["questions"][0]["text"] == "What is 2+2?"
