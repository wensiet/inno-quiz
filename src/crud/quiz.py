from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.quiz import Question, Quiz, QuizResult
from src.models.user import User
from src.schemas.quiz import (QuestionCreate, QuestionUpdate, QuizCreate,
                              QuizResultCreate, QuizUpdate)


def get_quiz(db: Session, quiz_id: int) -> Quiz:
    """Get a quiz by ID."""
    db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not db_quiz:
        return None

    # Always return quiz with questions loaded for now
    db_quiz = db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .filter(Quiz.id == db_quiz.id)
    ).scalars().first()

    return db_quiz


def get_quizzes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    author_id: int | None = None,
) -> list[Quiz]:
    """Get all quizzes, optionally filtered by author."""
    query = select(Quiz).options(
        selectinload(Quiz.questions),
        selectinload(Quiz.author),
    )
    if author_id:
        query = query.filter(Quiz.author_id == author_id)
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().all()


def create_quiz(db: Session, quiz: QuizCreate, author_id: int) -> Quiz:
    """Create a new quiz."""
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        is_public=quiz.is_public,
        author_id=author_id,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)

    # Add questions if provided
    if quiz.questions:
        for question_data in quiz.questions:
            create_question(db, question_data, db_quiz.id)

    # Reload the quiz with questions eagerly loaded
    query = (
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .filter(Quiz.id == db_quiz.id)
    )
    result = db.execute(query)
    return result.scalars().first()


def update_quiz(db: Session, quiz_id: int, quiz: QuizUpdate) -> Quiz | None:
    """Update a quiz."""
    db_quiz = get_quiz(db, quiz_id)
    if not db_quiz:
        return None

    update_data = quiz.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_quiz, key, value)

    db.commit()
    db.refresh(db_quiz)
    return db_quiz


def delete_quiz(db: Session, quiz_id: int) -> Quiz | None:
    """Delete a quiz."""
    db_quiz = get_quiz(db, quiz_id)
    if not db_quiz:
        return None

    db.delete(db_quiz)
    db.commit()
    return db_quiz


# Question CRUD operations
def get_question(db: Session, question_id: int) -> Question | None:
    """Get a question by ID."""
    query = select(Question).filter(Question.id == question_id)
    result = db.execute(query)
    return result.scalars().first()


def get_questions(db: Session, quiz_id: int) -> list[Question]:
    """Get all questions for a quiz."""
    query = select(Question).filter(Question.quiz_id == quiz_id)
    result = db.execute(query)
    return result.scalars().all()


def create_question(
    db: Session, question: QuestionCreate, quiz_id: int
) -> Question:
    """Create a new question for a quiz."""
    db_question = Question(
        quiz_id=quiz_id,
        text=question.text,
        options=question.options,
        correct_answer=question.correct_answer,
        points=question.points,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def update_question(
    db: Session,
    question_id: int,
    question: QuestionUpdate,
) -> Question | None:
    """Update a question."""
    db_question = get_question(db, question_id)
    if not db_question:
        return None

    update_data = question.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_question, key, value)

    db.commit()
    db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int) -> Question | None:
    """Delete a question."""
    db_question = get_question(db, question_id)
    if not db_question:
        return None

    db.delete(db_question)
    db.commit()
    return db_question


# Quiz result CRUD operations
def get_quiz_result(db: Session, result_id: int) -> QuizResult | None:
    """Get a quiz result by ID."""
    query = select(QuizResult).filter(QuizResult.id == result_id)
    result = db.execute(query)
    return result.scalars().first()


def get_quiz_results(
    db: Session,
    quiz_id: int | None = None,
    user_id: int | None = None,
) -> list[QuizResult]:
    """Get all quiz results, optionally filtered by quiz or user."""
    query = select(QuizResult)
    if quiz_id:
        query = query.filter(QuizResult.quiz_id == quiz_id)
    if user_id:
        query = query.filter(QuizResult.user_id == user_id)
    result = db.execute(query)
    return result.scalars().all()


def get_user_results(db: Session, user_id: int) -> list[QuizResult]:
    """Get all quiz results for a specific user."""
    return get_quiz_results(db, user_id=user_id)


def create_quiz_result(
    db: Session,
    result_in: QuizResultCreate,
    quiz_id: int,
    user_id: int,
) -> QuizResult:
    """Create a new quiz result."""
    # Process answers and calculate score
    from src.models.quiz import Question

    # Get all questions for the quiz to check answers
    query = select(Question).filter(Question.quiz_id == quiz_id)
    questions = db.execute(query).scalars().all()

    # Build a dictionary of question_id -> correct_answer for easier lookup
    correct_answers = {q.id: q.correct_answer for q in questions}
    question_points = {q.id: q.points for q in questions}

    # Calculate score
    score = 0
    max_score = sum(question_points.values())
    correct_count = 0

    # Store answers in a dictionary format that can be serialized to JSON
    answers_dict = {}

    for answer in result_in.answers:
        question_id = answer.question_id
        str_question_id = str(question_id)
        user_answer = answer.answer
        answers_dict[str_question_id] = user_answer

        # Check if this answer is correct
        if (
            question_id in correct_answers
            and user_answer == correct_answers[question_id]
        ):
            score += question_points.get(question_id, 0)
            correct_count += 1

    # Create the result
    db_result = QuizResult(
        quiz_id=quiz_id,
        user_id=user_id,
        score=score,
        max_score=max_score,
        correct_answers=correct_count,
        answers=answers_dict,
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_quiz_leaderboard(
    db: Session, quiz_id: int, limit: int = 10
) -> list[dict]:
    """Get the leaderboard for a quiz."""
    results = (
        db.query(
            User.username,
            QuizResult.score,
            QuizResult.max_score,
            (QuizResult.score * 100 / QuizResult.max_score).label(
                "percentage"
            ),
            QuizResult.completed_at,
        )
        .join(User)
        .filter(QuizResult.quiz_id == quiz_id)
        .order_by(QuizResult.score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "username": result[0],
            "score": result[1],
            "max_score": result[2],
            "percentage": result[3],
            "completed_at": result[4],
        }
        for result in results
    ]
