from enum import StrEnum
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.responses import Response


class ErrorCode(StrEnum):
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNAUTHORIZED = "UNAUTHORIZED"
    BAD_REQUEST = "BAD_REQUEST"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return cls.UNKNOWN


class HttpError(HTTPException):
    status_code: int = NotImplemented
    detail: str = "Http exception."

    def __init__(self, detail: str = "") -> None:
        super().__init__(status_code=self.status_code, detail=detail or self.detail)


class ForbiddenError(HttpError):
    status_code = 403


class NotFoundError(HttpError):
    status_code = 404


class ConflictError(HttpError):
    status_code = 409


class UnauthorizedError(HttpError):
    status_code = 401


class BadRequestError(HttpError):
    status_code = 400


class APIErrorResponse(BaseModel):
    id: str
    message: str
    system_error: str | None
    error_code: ErrorCode


def http_exception_handler(_: Request, exc: HTTPException) -> Response:
    return JSONResponse(
        status_code=exc.status_code,
        content=APIErrorResponse(
            id=str(uuid4()),
            message="Something went wrong",
            system_error=exc.detail,
            error_code=ErrorCode(
                {
                    400: ErrorCode.BAD_REQUEST,
                    401: ErrorCode.UNAUTHORIZED,
                    403: ErrorCode.FORBIDDEN,
                    404: ErrorCode.NOT_FOUND,
                    409: ErrorCode.CONFLICT,
                }.get(exc.status_code, "UNKNOWN")
            ),
        ).model_dump(),
    )
