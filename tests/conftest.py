"""Pytest configuration file for tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.auth.utils import create_access_token, get_password_hash
from src.main import create_app
from src.models.base import Base
from src.models.quiz import Question, Quiz
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


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency with test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create the test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> TestClient:
    """Create a test client with the test database."""
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_superuser=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user: User) -> str:
    """Create a token for the test user."""
    return create_access_token({"sub": test_user.username, "scopes": ["user"]})


@pytest.fixture
def admin_token(test_admin: User) -> str:
    """Create a token for the test admin."""
    return create_access_token(
        {"sub": test_admin.username, "scopes": ["user", "admin"]}
    )


@pytest.fixture
def test_quiz(db: Session, test_user: User) -> Quiz:
    """Create a test quiz."""
    quiz = Quiz(
        title="Test Quiz",
        description="A quiz for testing",
        is_public=True,
        author_id=test_user.id,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # Add some questions
    questions = [
        Question(
            quiz_id=quiz.id,
            text="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer="4",
            points=1,
        ),
        Question(
            quiz_id=quiz.id,
            text="What is the capital of France?",
            options=["London", "Berlin", "Paris", "Madrid"],
            correct_answer="Paris",
            points=2,
        ),
    ]
    db.add_all(questions)
    db.commit()

    # Reload the quiz to include the questions
    db.refresh(quiz)
    return quiz
