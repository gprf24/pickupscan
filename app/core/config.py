# app/core/config.py
"""
Application configuration using pydantic-settings.

Loads values from environment variables and .env file.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object for the app.
    All attributes can be overridden via environment variables.
    """

    # Application name (used in FastAPI title, etc.)
    app_name: str = "pickupscan"

    # Secret key for signing session cookies (Starlette SessionMiddleware).
    # IMPORTANT: change this in production to a long random string.
    secret_key: str = "CHANGE_ME_TO_RANDOM_SECRET"

    # SQLAlchemy / SQLModel database URL.
    # Example for Postgres:
    # postgresql+psycopg://user:password@host:5432/dbname
    database_url: str = "postgresql+psycopg://user:pass@localhost:5432/pickupscan"

    # pydantic v2 way to configure settings source (env files, etc.)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Avoids re-reading environment variables on every call.
    """
    return Settings()
