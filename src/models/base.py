from typing import ClassVar

from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped


class Base(DeclarativeBase):
    """Base class for all models."""

    created_at: Mapped[DateTime] = Column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __abstract__ = True
    __name__: ClassVar[str]

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate tablename automatically."""
        return cls.__name__.lower()
