from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class GenericListResponse(BaseModel, Generic[T]):
    count: int
    items: list[T]
