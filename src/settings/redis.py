from pydantic import Field
from pydantic_settings import BaseSettings

from src.utils.base.settings import get_base_config


class RedisSettings(BaseSettings):
    host: str = Field("localhost", description="Redis host")
    port: int = Field(6379, description="Redis port")
    password: str = Field("password", description="Redis password")
    database: int = Field(0, description="Redis database")

    @property
    def broker_dsn(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"

    model_config = get_base_config("redis_")


redis_settings = RedisSettings()
