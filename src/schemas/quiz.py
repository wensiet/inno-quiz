from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class QuestionBase(BaseModel):
    """Base question schema."""

    text: str
    options: list[str]
    correct_answer: str
    points: int = 1

    @model_validator(mode="after")
    def validate_correct_answer(self) -> "QuestionBase":
        """Validate that correct answer is in options."""
        if self.correct_answer not in self.options:
            raise ValueError("Correct answer must be one of the options")
        return self


class QuestionCreate(QuestionBase):
    """Schema for question creation."""


class QuestionUpdate(BaseModel):
    """Schema for question update."""

    text: str | None = None
    options: list[str] | None = None
    correct_answer: str | None = None
    points: int | None = None

    @model_validator(mode="after")
    def validate_correct_answer(self) -> "QuestionUpdate":
        """Validate that correct answer is in options if both are provided."""
        if self.correct_answer is not None and self.options is not None:
            if self.correct_answer not in self.options:
                raise ValueError("Correct answer must be one of the options")
        return self


class QuestionInDB(QuestionBase):
    """Schema for question in database."""

    id: int
    quiz_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class QuestionResponse(QuestionInDB):
    """Schema for question response."""


class QuizBase(BaseModel):
    """Base quiz schema."""

    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    is_public: bool = True


class QuizCreate(QuizBase):
    """Schema for quiz creation."""

    questions: list[QuestionCreate] | None = None


class QuizUpdate(BaseModel):
    """Schema for quiz update."""

    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class QuizInDB(QuizBase):
    """Schema for quiz in database."""

    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class QuizResponse(QuizInDB):
    """Schema for quiz response."""

    questions: list[QuestionResponse] = []
    author_username: str | None = None


class QuizAnswer(BaseModel):
    """Schema for quiz answer."""

    question_id: int
    answer: str


class QuizSubmission(BaseModel):
    """Schema for quiz submission."""

    quiz_id: int
    answers: list[QuizAnswer]


class QuizResultCreate(BaseModel):
    """Schema for creating quiz results."""

    answers: list[QuizAnswer]


class QuizResultBase(BaseModel):
    """Base quiz result schema."""

    quiz_id: int
    user_id: int
    score: int
    max_score: int
    answers: dict[str, str]  # question_id -> answer


class QuizResultInDB(QuizResultBase):
    """Schema for quiz result in database."""

    id: int
    completed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class QuizResultResponse(QuizResultInDB):
    """Schema for quiz result response."""

    username: str | None = None
    quiz_title: str | None = None
    correct_answers: int | None = None


class LeaderboardEntry(BaseModel):
    """Schema for leaderboard entry."""

    username: str
    score: int
    max_score: int
    percentage: float
    completed_at: datetime


class LeaderboardResponse(BaseModel):
    """Schema for leaderboard response."""

    quiz_id: int
    quiz_title: str
    entries: list[LeaderboardEntry]
