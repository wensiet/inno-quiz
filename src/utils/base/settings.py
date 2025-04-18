from pydantic_settings import SettingsConfigDict


def get_base_config(env_prefix: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_file=".env",
        env_prefix=env_prefix,
        extra="ignore",
        env_file_encoding="utf-8",
    )
