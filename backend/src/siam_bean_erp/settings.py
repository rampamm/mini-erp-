import os

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET = "local-dev-only-secret-change-me-before-deploy"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://erp:erp@localhost:54329/erp"
    jwt_secret: str = DEFAULT_JWT_SECRET
    token_ttl_hours: int = 12

    @model_validator(mode="after")
    def deployed_apps_need_their_own_secret(self) -> "Settings":
        if os.environ.get("VERCEL") and self.jwt_secret == DEFAULT_JWT_SECRET:
            raise ValueError("Set JWT_SECRET to a long random value before deploying")
        return self


def get_settings() -> Settings:
    return Settings()
