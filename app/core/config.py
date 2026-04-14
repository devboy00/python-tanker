from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Tanker API"
    app_env: str = "development"
    secret_key: str = "change-me"
    database_url: str = "postgresql+psycopg://tanker_user:change_me@localhost:5432/tanker"
    initial_superadmin_email: str = "admin@example.com"
    initial_superadmin_password: str = "change-me-now"
    site_name: str = "Tanker"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
