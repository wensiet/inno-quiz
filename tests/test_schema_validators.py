"""Tests for schema validators."""

import pytest
from pydantic import ValidationError

from src.schemas.quiz import QuestionBase, QuestionUpdate


def test_question_correct_answer_validation():
    """Test that QuestionBase validates that correct_answer is in options."""
    # Valid case
    question = QuestionBase(
        text="What is 2+2?",
        options=["3", "4", "5", "6"],
        correct_answer="4",
        points=1,
    )
    assert question.correct_answer == "4"

    # Invalid case
    with pytest.raises(ValidationError) as excinfo:
        QuestionBase(
            text="What is 2+2?",
            options=["3", "4", "5", "6"],
            correct_answer="7",  # Not in options
            points=1,
        )

    # Ensure the error message is clear
    assert "Correct answer must be one of the options" in str(excinfo.value)


def test_question_update_validation():
    """Test that QuestionUpdate validates correct_answer is in options if both are provided."""
    # Valid case - providing both options and correct_answer
    question_update = QuestionUpdate(
        text="Updated question",
        options=["A", "B", "C"],
        correct_answer="B",
        points=2,
    )
    assert question_update.correct_answer == "B"

    # Valid case - providing only options
    question_update = QuestionUpdate(
        options=["A", "B", "C"],
    )
    assert question_update.options == ["A", "B", "C"]

    # Valid case - providing only correct_answer
    question_update = QuestionUpdate(
        correct_answer="X",
    )
    assert question_update.correct_answer == "X"

    # Invalid case - correct_answer not in options
    with pytest.raises(ValidationError) as excinfo:
        QuestionUpdate(
            options=["A", "B", "C"],
            correct_answer="X",  # Not in options
        )

    # Ensure the error message is clear
    assert "Correct answer must be one of the options" in str(excinfo.value)
