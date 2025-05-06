import datetime
import uuid
from collections.abc import Generator
from contextlib import contextmanager

import sqlalchemy
from sqlalchemy import Boolean, Column, String, create_engine
from sqlalchemy.orm import Mapped, Session, mapped_column, sessionmaker

try:
    from src.settings.database_override import \
        sqlite_database_settings as database_settings
except ImportError:
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


# Use standard database URL
db_url = database_settings.dsn

# Configure engine based on database type
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Provide a database session."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
