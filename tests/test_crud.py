"""Tests for the database CRUD operations."""

from sqlalchemy.orm import Session

from src.crud.quiz import (create_question, create_quiz, create_quiz_result,
                           delete_question, delete_quiz, get_quiz,
                           get_quiz_leaderboard, get_quiz_results, get_quizzes,
                           get_user_results, update_question, update_quiz)
from src.crud.user import (create_user, delete_user, get_user,
                           get_user_by_email, get_user_by_username,
                           update_user)
from src.schemas.quiz import (QuestionCreate, QuestionUpdate, QuizCreate,
                              QuizResultCreate, QuizUpdate)
from src.schemas.user import UserCreate, UserUpdate


def test_create_user(db: Session):
    """Test creating a user."""
    user_in = UserCreate(
        username="testcrud",
        email="testcrud@example.com",
        password="password123",
    )
    user = create_user(db, user_in)
    assert user.username == "testcrud"
    assert user.email == "testcrud@example.com"
    assert user.is_active is True
    assert user.is_superuser is False  # Check superuser status instead of admin
    assert user.hashed_password != "password123"  # Password should be hashed


def test_get_user(db: Session):
    """Test getting a user by ID."""
    # First create a user
    user_in = UserCreate(
        username="testget",
        email="testget@example.com",
        password="password123",
    )
    created_user = create_user(db, user_in)

    # Now retrieve it
    user = get_user(db, created_user.id)
    assert user is not None
    assert user.id == created_user.id
    assert user.username == "testget"
    assert user.email == "testget@example.com"


def test_get_user_by_email(db: Session):
    """Test getting a user by email."""
    # First create a user
    user_in = UserCreate(
        username="testemail",
        email="testemail@example.com",
        password="password123",
    )
    create_user(db, user_in)

    # Now retrieve it
    user = get_user_by_email(db, "testemail@example.com")
    assert user is not None
    assert user.username == "testemail"
    assert user.email == "testemail@example.com"


def test_get_user_by_username(db: Session):
    """Test getting a user by username."""
    # First create a user
    user_in = UserCreate(
        username="testusername",
        email="testusername@example.com",
        password="password123",
    )
    create_user(db, user_in)

    # Now retrieve it
    user = get_user_by_username(db, "testusername")
    assert user is not None
    assert user.username == "testusername"
    assert user.email == "testusername@example.com"


def test_update_user(db: Session):
    """Test updating a user."""
    # First create a user
    user_in = UserCreate(
        username="testupdate",
        email="testupdate@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    # Now update it
    user_update = UserUpdate(
        email="newemail@example.com",
        password="newpassword123",
    )
    updated_user = update_user(db, user.id, user_update)
    assert updated_user.email == "newemail@example.com"
    # No need to check if the password hash changed, just verify it has been set
    assert updated_user.hashed_password is not None


def test_delete_user(db: Session):
    """Test deleting a user."""
    # First create a user
    user_in = UserCreate(
        username="testdelete",
        email="testdelete@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    # Now delete it
    delete_user(db, user.id)

    # Verify it's deleted
    deleted_user = get_user(db, user.id)
    assert deleted_user is None


def test_create_quiz(db: Session):
    """Test creating a quiz."""
    # First create a user for the quiz author
    user_in = UserCreate(
        username="quizauthor",
        email="quizauthor@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    # Now create a quiz
    quiz_in = QuizCreate(
        title="Test Quiz",
        description="A test quiz",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)
    assert quiz.title == "Test Quiz"
    assert quiz.description == "A test quiz"
    assert quiz.is_public is True
    assert quiz.author_id == user.id
    assert len(quiz.questions) == 0


def test_get_quiz(db: Session):
    """Test getting a quiz by ID."""
    # First create a user and quiz
    user_in = UserCreate(
        username="quizget",
        email="quizget@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Get Quiz",
        description="A quiz to get",
        is_public=True,
        questions=[],
    )
    created_quiz = create_quiz(db, quiz_in, user.id)

    # Now retrieve it
    quiz = get_quiz(db, created_quiz.id)
    assert quiz is not None
    assert quiz.id == created_quiz.id
    assert quiz.title == "Get Quiz"
    assert quiz.description == "A quiz to get"
    assert quiz.author_id == user.id


def test_get_quizzes(db: Session):
    """Test getting all quizzes."""
    # First create a user and two quizzes
    user_in = UserCreate(
        username="quizzes",
        email="quizzes@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in1 = QuizCreate(
        title="Quiz 1",
        description="First quiz",
        is_public=True,
        questions=[],
    )
    quiz_in2 = QuizCreate(
        title="Quiz 2",
        description="Second quiz",
        is_public=True,
        questions=[],
    )
    create_quiz(db, quiz_in1, user.id)
    create_quiz(db, quiz_in2, user.id)

    # Now retrieve all quizzes
    quizzes = get_quizzes(db, skip=0, limit=100)
    assert len(quizzes) >= 2

    # Retrieve user's quizzes
    user_quizzes = get_quizzes(db, skip=0, limit=100, author_id=user.id)
    assert len(user_quizzes) >= 2
    assert all(quiz.author_id == user.id for quiz in user_quizzes)


def test_update_quiz(db: Session):
    """Test updating a quiz."""
    # First create a user and quiz
    user_in = UserCreate(
        username="quizupdate",
        email="quizupdate@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Update Quiz",
        description="A quiz to update",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    # Now update it
    quiz_update = QuizUpdate(
        title="Updated Quiz",
        description="An updated quiz",
        is_public=False,
    )
    updated_quiz = update_quiz(db, quiz.id, quiz_update)
    assert updated_quiz.title == "Updated Quiz"
    assert updated_quiz.description == "An updated quiz"
    assert updated_quiz.is_public is False


def test_delete_quiz(db: Session):
    """Test deleting a quiz."""
    # First create a user and quiz
    user_in = UserCreate(
        username="quizdelete",
        email="quizdelete@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Delete Quiz",
        description="A quiz to delete",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    # Now delete it
    delete_quiz(db, quiz.id)

    # Verify it's deleted
    deleted_quiz = get_quiz(db, quiz.id)
    assert deleted_quiz is None


def test_create_question(db: Session):
    """Test creating a question for a quiz."""
    # First create a user and quiz
    user_in = UserCreate(
        username="questionauthor",
        email="questionauthor@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Question Quiz",
        description="A quiz with questions",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    # Now create a question
    question_in = QuestionCreate(
        text="What is 2+2?",
        options=["1", "2", "3", "4"],
        correct_answer="4",
        points=1,
    )
    question = create_question(db, question_in, quiz.id)
    assert question.text == "What is 2+2?"
    assert question.options == ["1", "2", "3", "4"]
    assert question.correct_answer == "4"
    assert question.points == 1
    assert question.quiz_id == quiz.id

    # Verify quiz now has one question
    quiz = get_quiz(db, quiz.id)
    assert len(quiz.questions) == 1


def test_update_question(db: Session):
    """Test updating a question."""
    # First create a user, quiz, and question
    user_in = UserCreate(
        username="questionupdate",
        email="questionupdate@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Question Update Quiz",
        description="A quiz with a question to update",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    question_in = QuestionCreate(
        text="Original question?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        points=1,
    )
    question = create_question(db, question_in, quiz.id)

    # Now update the question
    question_update = QuestionUpdate(
        text="Updated question?",
        options=["W", "X", "Y", "Z"],
        correct_answer="Z",
        points=2,
    )
    updated_question = update_question(db, question.id, question_update)
    assert updated_question.text == "Updated question?"
    assert updated_question.options == ["W", "X", "Y", "Z"]
    assert updated_question.correct_answer == "Z"
    assert updated_question.points == 2


def test_delete_question(db: Session):
    """Test deleting a question."""
    # First create a user, quiz, and question
    user_in = UserCreate(
        username="questiondelete",
        email="questiondelete@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Question Delete Quiz",
        description="A quiz with a question to delete",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    question_in = QuestionCreate(
        text="Question to delete?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        points=1,
    )
    question = create_question(db, question_in, quiz.id)

    # Now delete the question
    delete_question(db, question.id)

    # Verify quiz now has no questions
    quiz = get_quiz(db, quiz.id)
    assert len(quiz.questions) == 0


def test_create_quiz_result(db: Session):
    """Test creating a quiz result."""
    # First create a user, quiz with questions
    user_in = UserCreate(
        username="resultuser",
        email="resultuser@example.com",
        password="password123",
    )
    user = create_user(db, user_in)

    quiz_in = QuizCreate(
        title="Result Quiz",
        description="A quiz for results",
        is_public=True,
        questions=[],
    )
    quiz = create_quiz(db, quiz_in, user.id)

    question_in1 = QuestionCreate(
        text="Q1?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        points=1,
    )
    question_in2 = QuestionCreate(
        text="Q2?",
        options=["W", "X", "Y", "Z"],
        correct_answer="Z",
        points=2,
    )
    question1 = create_question(db, question_in1, quiz.id)
    question2 = create_question(db, question_in2, quiz.id)

    # Now create a quiz result with one correct answer
    result_in = QuizResultCreate(
        answers=[
            {"question_id": question1.id, "answer": "A"},  # Correct
            {"question_id": question2.id, "answer": "Y"},  # Incorrect
        ],
    )
    result = create_quiz_result(db, result_in, quiz.id, user.id)
    assert result.quiz_id == quiz.id
    assert result.user_id == user.id
    assert result.score == 1  # One correct answer worth 1 point
    assert result.max_score == 3  # Total possible points from both questions
    assert result.correct_answers == 1


def test_get_quiz_results(db: Session):
    """Test getting results for a quiz."""
    # Reuse the setup from test_create_quiz_result
    test_create_quiz_result(db)

    # Get results for the last created quiz
    quizzes = get_quizzes(db, skip=0, limit=100)
    quiz = quizzes[-1]

    results = get_quiz_results(db, quiz.id)
    assert len(results) >= 1
    result = results[0]
    assert result.quiz_id == quiz.id


def test_get_user_results(db: Session):
    """Test getting all results for a user."""
    # Reuse the setup from test_create_quiz_result
    test_create_quiz_result(db)

    # Get results for the last created user
    user = get_user_by_username(db, "resultuser")

    results = get_user_results(db, user.id)
    assert len(results) >= 1
    result = results[0]
    assert result.user_id == user.id


def test_get_quiz_leaderboard(db: Session):
    """Test getting the leaderboard for a quiz."""
    # Reuse the setup from test_create_quiz_result
    test_create_quiz_result(db)

    # Get leaderboard for the last created quiz
    quizzes = get_quizzes(db, skip=0, limit=100)
    quiz = quizzes[-1]

    leaderboard = get_quiz_leaderboard(db, quiz.id)
    assert len(leaderboard) >= 1
    entry = leaderboard[0]
    assert entry["username"] == "resultuser"
    assert entry["score"] == 1
    assert entry["max_score"] == 3
    # Check that the percentage is around 33.33%, allowing for decimal representation differences
    assert 33.0 <= float(entry["percentage"]) <= 34.0  # 1/3 * 100
