from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://erp:erp@localhost:54329/erp"
    jwt_secret: str = "local-dev-only-secret-change-me-before-deploy"
    token_ttl_hours: int = 12


def get_settings() -> Settings:
    return Settings()
