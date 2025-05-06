from pydantic import Field
from pydantic_settings import BaseSettings

from src.utils.base.settings import get_base_config


class SqliteDatabaseSettings(BaseSettings):
    database_path: str = Field(
        "./inno_quiz.db",
        description="SQLite database path"
    )

    @property
    def dsn(self) -> str:
        return f"sqlite:///{self.database_path}"

    @property
    def celery_dsn(self) -> str:
        return f"db+sqlite:///{self.database_path}"

    model_config = get_base_config("db_")


sqlite_database_settings = SqliteDatabaseSettings()

# Alias for compatibility
database_settings = sqlite_database_settings
