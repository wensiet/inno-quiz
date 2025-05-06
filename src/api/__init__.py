"""
API routers.
"""

from fastapi import APIRouter

from src.api import auth, questions, quiz_results, quizzes, trivia, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(
    questions.router, prefix="/quizzes/{quiz_id}/questions", tags=["questions"]
)
api_router.include_router(
    quiz_results.router,
    prefix="/quizzes/{quiz_id}/results",
    tags=["quiz results"]
)
api_router.include_router(
    quiz_results.user_results_router,
    prefix="/quizzes/results",
    tags=["user results"]
)
api_router.include_router(trivia.router, prefix="/trivia", tags=["trivia"])
