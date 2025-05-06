"""
API routers.
"""

from fastapi import APIRouter

from src.api import auth, questions, quiz_results, quizzes, trivia, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
