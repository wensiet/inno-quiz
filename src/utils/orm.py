import datetime
import uuid
from collections.abc import Generator
from contextlib import contextmanager

import sqlalchemy
from sqlalchemy import Boolean, Column, QueuePool, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.settings.database import database_settings


class Base(sqlalchemy.orm.DeclarativeBase):
    pass


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=sqlalchemy.func.now(),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    )


class UUIDMixin:
    id = Column(String, primary_key=True, default=uuid.uuid4)


class AvailableMixin:
    available = Column(Boolean, default=True, nullable=False)


engine = sqlalchemy.create_engine(
    database_settings.dsn,
    poolclass=QueuePool,
    pool_size=database_settings.pool_size,
    pool_timeout=database_settings.pool_timeout,
    max_overflow=database_settings.max_overflow,
)


def session_factory() -> Session:
    return sqlalchemy.orm.sessionmaker(bind=engine)()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
