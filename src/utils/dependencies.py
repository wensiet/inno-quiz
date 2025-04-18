from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.utils.exceptions import UnauthorizedError
from src.utils.orm import session_scope

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,
)


def get_session() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session


def get_current_user_id(
    bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not bearer:
        raise UnauthorizedError(detail="No credentials provided")
    token = bearer.credentials  # noqa: F841
    raise NotImplementedError("Implement authorization logic")


CURRENT_USER_ID_DEPENDENCY = Annotated[int, Depends(get_current_user_id)]
