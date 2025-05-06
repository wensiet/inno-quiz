from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.utils.exceptions import UnauthorizedError
from src.utils.orm import get_db_session

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,
)


def get_db() -> Generator[Session, None, None]:
    """Get a database session."""
    with get_db_session() as session:
        yield session


def get_current_user_id(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not bearer:
        raise UnauthorizedError(detail="No credentials provided")
    token = bearer.credentials  # noqa: F841
    raise NotImplementedError("Implement authorization logic")


CURRENT_USER_ID_DEPENDENCY = Annotated[int, Depends(get_current_user_id)]
