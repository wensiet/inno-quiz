from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import get_current_active_user
from src.crud.quiz import (create_quiz_result, get_questions,
                           get_quiz, get_quiz_results as get_results_db,
                           get_quiz_leaderboard as get_leaderboard_db,
                           get_user_results)
from src.models.user import User
from src.schemas.quiz import (LeaderboardEntry, LeaderboardResponse,
                              QuizResultCreate, QuizResultResponse)
from src.utils.dependencies import get_db

router = APIRouter()
user_results_router = APIRouter()


@router.post(
    "/",
    response_model=QuizResultResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_quiz_result(
    quiz_id: int,
    quiz_result_create: QuizResultCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Submit a quiz result with answers."""
    # Check if quiz exists
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Validate all questions exists in this quiz
    answers = quiz_result_create.answers
    question_ids = [answer.question_id for answer in answers]
    db_questions = get_questions(db, quiz_id)
    db_question_ids = [q.id for q in db_questions]

    # Find invalid question IDs
    invalid_q = []
    for qid in question_ids:
        if qid not in db_question_ids:
            invalid_q.append(qid)

    if invalid_q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Questions with IDs {invalid_q} not found in quiz",
        )

    # Create the quiz result
    result = create_quiz_result(
        db, quiz_result_create, quiz.id, current_user.id
    )
    return result


@user_results_router.get("/user", response_model=list[QuizResultResponse])
def get_my_quiz_results(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get all quiz results for the current user."""
    results = get_user_results(db, current_user.id)

    # Get quiz titles
    for result in results:
        quiz = get_quiz(db, result.quiz_id)
        result.quiz_title = quiz.title if quiz else "Unknown Quiz"
        result.username = (
            result.user.username if result.user else "Unknown User"
        )

    return results


@router.get("/", response_model=list[QuizResultResponse])
def get_quiz_results(
    quiz_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get results for a specific quiz. Only the author can see these."""
    # Check if quiz exists
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Check if user is quiz author
    if quiz.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    results = get_results_db(db, quiz_id)
    return results


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_quiz_leaderboard(
    quiz_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """Get leaderboard for a quiz. Only available for public quizzes."""
    # Check if quiz exists and is public
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if not quiz.is_public:
        raise HTTPException(
            status_code=403,
            detail="Leaderboard available only for public quizzes",
        )

    leaderboard = get_leaderboard_db(db, quiz_id)
    entries = []
    for item in leaderboard:
        entries.append(
            LeaderboardEntry(
                username=item["username"],
                score=item["score"],
                max_score=item["max_score"],
                percentage=item["percentage"],
                completed_at=item["completed_at"],
            )
        )

    return LeaderboardResponse(
        quiz_id=quiz_id, quiz_title=quiz.title, entries=entries
    )
