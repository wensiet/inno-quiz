import re
from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from src.settings.database import sqlite_database_settings as database_settings
from src.utils.orm import Base

# from celery.backends.database.session import ResultModelBase  # noqa: ERA001

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):  # noqa: ANN001, ANN201, A002
    """
    Should you include this table or not?
    """

    if (
        type_ == "table"
        and (
            re.match(
                "celery_*",
                name,
            )
            or object.info.get("skip_autogenerate", False)
        )
    ) or (type_ == "column" and object.info.get("skip_autogenerate", False)):
        return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=database_settings.dsn,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online(connection) -> None:  # noqa: ANN001
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migration_with_engine(engine):  # noqa: ANN001, ANN201
    with engine.connect() as connection:
        run_migrations_online(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migration_with_engine(create_engine(database_settings.dsn))
