from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import get_current_active_user
from src.crud.quiz import (create_quiz, delete_quiz, get_quiz, get_quizzes,
                           update_quiz)
from src.models.user import User
from src.schemas.quiz import QuizCreate, QuizResponse, QuizUpdate
from src.utils.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=list[QuizResponse])
def read_quizzes(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    skip: int = 0,
    limit: int = 100,
    my_quizzes: bool = False,
) -> Any:
    """Get all quizzes. If my_quizzes is true, get only the user's quizzes."""
    author_id = current_user.id if my_quizzes else None
    quizzes = get_quizzes(db, skip=skip, limit=limit, author_id=author_id)
    return quizzes


@router.get("/{quiz_id}", response_model=QuizResponse)
def read_quiz(
    quiz_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get a specific quiz."""
    quiz = get_quiz(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post(
    "/",
    response_model=QuizResponse,
    status_code=status.HTTP_201_CREATED
)
def create_quiz_endpoint(
    quiz_in: QuizCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Create a new quiz."""
    quiz = create_quiz(db, quiz_in, current_user.id)
    return quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz_endpoint(
    quiz_id: int,
    quiz_in: QuizUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Update a quiz. Only the author can update it."""
    quiz = get_quiz(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check if the user is the author of the quiz
    if quiz.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_quiz = update_quiz(db, quiz_id, quiz_in)
    return updated_quiz


@router.delete("/{quiz_id}", status_code=status.HTTP_200_OK)
def delete_quiz_endpoint(
    quiz_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Delete a quiz. Only the author can delete it."""
    quiz = get_quiz(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check if the user is the author of the quiz
    if quiz.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    delete_quiz(db, quiz_id)
    return {"detail": "Quiz deleted successfully"}
