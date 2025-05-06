from sqlalchemy import (JSON, Boolean, Column, DateTime, ForeignKey, Integer,
                        String, Text, func)
from sqlalchemy.orm import relationship

from src.models.base import Base


class Quiz(Base):
    """Quiz model."""

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    is_public = Column(Boolean, default=True)

    # Relationships
    author = relationship("User", backref="quizzes")
    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )
    results = relationship(
        "QuizResult", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    """Question model."""

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of possible answers
    correct_answer = Column(String(255), nullable=False)
    points = Column(Integer, default=1)  # Points awarded for correct answer

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class QuizResult(Base):
    """Quiz result model."""

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    correct_answers = Column(
        Integer, nullable=False, default=0
    )  # Number of correct answers
    answers = Column(
        JSON,
        nullable=False
    )  # User's answers with question_id -> answer
    completed_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="results")
    user = relationship("User", backref="quiz_results")
