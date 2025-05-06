from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import get_current_active_user
from src.crud.quiz import (create_question, delete_question, get_question,
                           get_questions, get_quiz, update_question)
from src.models.user import User
from src.schemas.quiz import QuestionCreate, QuestionResponse, QuestionUpdate
from src.utils.dependencies import get_db

router = APIRouter()


@router.get("/", response_model=list[QuestionResponse])
def read_questions(
    quiz_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get all questions for a quiz."""
    # Check if user has access to this quiz
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if not quiz.is_public and quiz.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    questions = get_questions(db, quiz_id)
    return questions


@router.post(
    "/",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_question_endpoint(
    quiz_id: int,
    question: QuestionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Create a new question for a quiz."""
    # Check if user is the author of the quiz or an admin
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    db_question = create_question(db, question, quiz_id)
    return db_question


@router.get("/{question_id}", response_model=QuestionResponse)
def read_question(
    quiz_id: int,
    question_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get a specific question by ID."""
    question = get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if user has access to the quiz this question belongs to
    quiz = get_quiz(db, question.quiz_id)
    if not quiz.is_public and quiz.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return question


@router.put("/{question_id}", response_model=QuestionResponse)
def update_question_endpoint(
    quiz_id: int,
    question_id: int,
    question_update: QuestionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Update a question. Only the quiz author or an admin can update it."""
    db_question = get_question(db, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if user is the author of the quiz or an admin
    quiz = get_quiz(db, db_question.quiz_id)
    if quiz.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_question = update_question(db, question_id, question_update)
    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")

    return updated_question


@router.delete("/{question_id}", status_code=status.HTTP_200_OK)
def delete_question_endpoint(
    quiz_id: int,
    question_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Delete a question. Only the quiz author or an admin can delete it."""
    db_question = get_question(db, question_id)
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if user is the author of the quiz or an admin
    quiz = get_quiz(db, db_question.quiz_id)
    if quiz.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    deleted_question = delete_question(db, question_id)
    if not deleted_question:
        raise HTTPException(status_code=404, detail="Question not found")

    return {"detail": "Question deleted successfully"}
