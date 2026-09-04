from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    ENVIRONMENT: Literal["development", "production"] = "development"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5435/event_ticketing"
    REDIS_URL: str = "redis://localhost:6382/0"

    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
