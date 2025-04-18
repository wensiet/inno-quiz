import urllib.parse

from pydantic import Field
from pydantic_settings import BaseSettings

from src.utils.base.settings import get_base_config


class DatabaseSettings(BaseSettings):
    host: str = Field("localhost", description="PostgreSQL host")
    port: int = Field(5432, description="PostgreSQL port")
    user: str = Field("user", description="PostgreSQL user")
    password: str = Field("password", description="PostgreSQL password")
    database: str = Field("fintech", description="PostgreSQL database")

    pool_size: int = Field(10, description="DB connection pool size")
    max_overflow: int = Field(20, description="DB connection pool overflow size")

    pool_timeout: int = Field(15, description="DB connection pool timeout")

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.user}:{urllib.parse.quote_plus(self.password)}@"
            f"{self.host}:{self.port}/{self.database}"
        )

    @property
    def celery_dsn(self) -> str:
        return f"db+postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    model_config = get_base_config("db_")


database_settings = DatabaseSettings()
