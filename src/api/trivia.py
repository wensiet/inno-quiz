from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import get_current_active_user
from src.crud.quiz import create_quiz
from src.external.trivia import (TriviaAPIException, fetch_trivia_questions,
                                 get_trivia_categories)
from src.schemas.quiz import QuestionCreate, QuizCreate, QuizResponse
from src.schemas.user import UserInDB
from src.utils.dependencies import get_db

router = APIRouter()


@router.get("/categories")
def get_categories() -> list[dict[str, str]]:
    """Get available trivia categories."""
    try:
        categories = get_trivia_categories()
        # Convert integer IDs to strings to fix validation error
        for category in categories:
            category["id"] = str(category["id"])
        return categories
    except TriviaAPIException as e:
        raise HTTPException(
            status_code=503,
            detail=f"External API error: {e!s}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}")


@router.get("/questions")
def get_trivia_questions(
    amount: int = 10,
    category: int | None = None,
    difficulty: str | None = None,
    type: str | None = None,
) -> list[QuestionCreate]:
    """Get random trivia questions from the Open Trivia DB.

    - **amount**: Number of questions (1-50)
    - **category**: Category ID (optional)
    - **difficulty**: easy, medium, hard (optional)
    - **type**: multiple, boolean (optional)
    """
    try:
        if amount < 1 or amount > 50:
            raise HTTPException(
                status_code=400,
                detail="Amount must be between 1 and 50",
            )

        questions = fetch_trivia_questions(
            amount=amount,
            category=category,
            difficulty=difficulty,
            question_type=type,
        )
        return questions
    except TriviaAPIException as e:
        raise HTTPException(
            status_code=503,
            detail=f"External API error: {e!s}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}")


@router.post(
    "/create-quiz", response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED
)
def create_trivia_quiz(
    title: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
    description: str | None = None,
    amount: int = 10,
    category: int | None = None,
    difficulty: str | None = None,
    type: str | None = None,
) -> QuizResponse:
    """Create a new quiz with random questions from the Open Trivia DB.

    - **title**: Quiz title
    - **description**: Quiz description (optional)
    - **amount**: Number of questions (1-50)
    - **category**: Category ID (optional)
    - **difficulty**: easy, medium, hard (optional)
    - **type**: multiple, boolean (optional)
    """
    try:
        if amount < 1 or amount > 50:
            raise HTTPException(
                status_code=400,
                detail="Amount must be between 1 and 50",
            )

        # Fetch questions from external API
        questions = fetch_trivia_questions(
            amount=amount,
            category=category,
            difficulty=difficulty,
            question_type=type,
        )

        # Create a new quiz with these questions
        quiz_create = QuizCreate(
            title=title,
            description=description,
            questions=questions,
            is_public=True,
        )

        db_quiz = create_quiz(db, quiz_create, current_user.id)

        # Create a clean dictionary from db_quiz excluding SQLAlchemy attributes
        quiz_data = {
            "id": db_quiz.id,
            "title": db_quiz.title,
            "description": db_quiz.description,
            "is_public": db_quiz.is_public,
            "author_id": db_quiz.author_id,
            "created_at": db_quiz.created_at,
            "updated_at": db_quiz.updated_at,
        }

        # Add questions data without using __dict__
        questions_data = []
        for q in db_quiz.questions:
            questions_data.append(
                {
                    "id": q.id,
                    "quiz_id": q.quiz_id,
                    "text": q.text,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "points": q.points,
                    "created_at": q.created_at,
                    "updated_at": q.updated_at,
                }
            )

        return QuizResponse(
            **quiz_data,
            questions=questions_data,
            author_username=current_user.username,
        )
    except TriviaAPIException as e:
        raise HTTPException(
            status_code=503,
            detail=f"External API error: {e!s}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e!s}")
