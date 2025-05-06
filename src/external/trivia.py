import html
import json
from typing import Any

import requests

from src.schemas.quiz import QuestionCreate


class TriviaAPIException(Exception):
    """Raised when there is an issue with the Trivia API."""


def fetch_trivia_questions(
    amount: int = 10,
    category: int | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
) -> list[QuestionCreate]:
    """Fetch trivia questions from Open Trivia DB API.

    Args:
        amount: Number of questions to fetch
        category: Category ID (see Open Trivia DB documentation)
        difficulty: Difficulty level (easy, medium, hard)
        question_type: Question type (multiple, boolean)

    Returns:
        List of QuestionCreate objects

    Raises:
        TriviaAPIException: If there is an issue with the API

    """
    url = "https://opentdb.com/api.php"

    # Build query params
    params = {"amount": amount}
    if category:
        params["category"] = category
    if difficulty:
        params["difficulty"] = difficulty
    if question_type:
        params["type"] = question_type

    try:
        response = requests.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        # Check response code
        if data["response_code"] == 0:
            # Success
            pass
        elif data["response_code"] == 1:
            # No Results
            error_msg = "No results found with the specified parameters"
            raise TriviaAPIException(error_msg)
        elif data["response_code"] == 2:
            # Invalid Parameter
            error_msg = "Invalid parameter in the API request"
            raise TriviaAPIException(error_msg)
        else:
            error_msg = (
                f"Unknown error code: {data['response_code']}",
            )
            raise TriviaAPIException(error_msg)

        questions = []
        for q in data["results"]:
            # Decode HTML entities
            question_text = html.unescape(q["question"])
            correct_answer = html.unescape(q["correct_answer"])
            incorrect_answers = [
                html.unescape(a) for a in q["incorrect_answers"]
            ]

            # Combine all options
            options = incorrect_answers + [correct_answer]

            question = QuestionCreate(
                text=question_text,
                options=options,
                correct_answer=correct_answer,
                points=1,
            )
            questions.append(question)

        return questions

    except requests.exceptions.RequestException as e:
        raise TriviaAPIException(f"HTTP error: {e!s}")
    except (json.JSONDecodeError, KeyError) as e:
        raise TriviaAPIException(f"Invalid response: {e!s}")
    except Exception as e:
        raise TriviaAPIException(f"Unexpected error: {e!s}")


def get_trivia_categories() -> list[dict[str, Any]]:
    """Get the list of available categories from the Open Trivia DB API.

    Returns:
        List of category objects with id and name

    Raises:
        TriviaAPIException: If there's an issue with the API

    """
    url = "https://opentdb.com/api_category.php"

    try:
        response = requests.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        return data["trivia_categories"]

    except requests.exceptions.RequestException as e:
        raise TriviaAPIException(f"HTTP error: {e!s}")
    except (json.JSONDecodeError, KeyError) as e:
        raise TriviaAPIException(f"Invalid response: {e!s}")
    except Exception as e:
        raise TriviaAPIException(f"Unexpected error: {e!s}")
