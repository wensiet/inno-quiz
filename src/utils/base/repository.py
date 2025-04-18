from __future__ import annotations

import datetime
import re
from decimal import Decimal
from typing import Any, Generic, TypeVar

import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql import operators

from src.utils.orm import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    orm_model: T

    def __init__(self, session: Session) -> None:
        self.session = session

    def _build_query(self, **filters: Any) -> sqlalchemy.Select:
        query = sqlalchemy.select(self.orm_model)  # type: ignore[arg-type]

        for key, value in filters.items():
            match = re.match(r"^(\w+)__(gt|ge|le|lt|like)$", key)
            if match:
                column_name, operator = match.groups()
                column = getattr(self.orm_model, column_name, None)

                if column is not None:
                    if operator == "like":
                        query = query.filter(column.like(value))
                    elif isinstance(value, (int | float | Decimal | datetime.datetime)):
                        op = {
                            "gt": operators.gt,
                            "ge": operators.ge,
                            "le": operators.le,
                            "lt": operators.lt,
                        }.get(operator)

                        if op:
                            query = query.filter(op(column, value))
                        else:
                            raise TypeError(f"Unsupported operator: {operator}")
                    else:
                        raise TypeError(f"Unsupported operator {operator} for column {key}")
                else:
                    raise AttributeError(
                        f"Column {column_name} not found in {self.orm_model.__name__}",
                    )
            elif isinstance(value, (list | tuple)):
                query = query.filter(getattr(self.orm_model, key).in_(value))
            else:
                query = query.filter(getattr(self.orm_model, key) == value)

        return query

    def get_by_attr(self, with_for_update: bool = False, **kwargs: Any) -> T:
        stmt = sqlalchemy.select(self.orm_model).filter_by(**kwargs)  # type: ignore[arg-type]
        if with_for_update:
            stmt = stmt.with_for_update()
        return self.session.execute(stmt).scalars().one()

    def get_by_attr_locked(self, **kwargs: Any) -> T:
        stmt = sqlalchemy.select(self.orm_model).filter_by(**kwargs).with_for_update()  # type: ignore[arg-type]
        return self.session.execute(stmt).scalars().one()

    def get_multi(self, limit: int = 10, offset: int = 0, **filters: Any) -> tuple[list[T], int]:
        query = self._build_query(**filters)
        stmt = query.limit(limit).offset(offset)
        results = self.session.execute(stmt).scalars().all()
        total = (
            self.session.execute(
                sqlalchemy.select(
                    sqlalchemy.func.count(),
                ),
            ).scalar()
            or 0
        )
        return list(results), total

    def save(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.flush()

    def update(self, obj: T) -> None:
        self.session.merge(obj)
        self.session.flush()
