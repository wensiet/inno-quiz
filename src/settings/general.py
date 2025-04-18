from pydantic import Field
from pydantic_settings import BaseSettings

from src.choices import Environment
from src.utils.base.settings import get_base_config


class GeneralSettings(BaseSettings):
    environment: Environment = Field(Environment.DEV)

    app_version: str | None = Field(None, description="App version")
    app_name: str = Field(..., description="Application name")
    app_description: str = Field(..., description="Short application description")

    ci_commit_short_sha: str | None = Field(None, description="Short commit SHA")

    @property
    def version(self) -> str:
        if self.app_version:
            return self.app_version
        if self.ci_commit_short_sha:
            return self.ci_commit_short_sha
        raise ValueError("No version specified")

    model_config = get_base_config("")


general_settings = GeneralSettings()
