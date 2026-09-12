from functools import lru_cache
import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    app_name: str = "BrandBridge AI API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://brandbridge:brandbridge@localhost:5432/brandbridge"

    jwt_secret: str = "change-me-in-development"
    jwt_algorithm: str = "HS256"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    llm_provider: str | None = None
    llm_api_key: str | None = None

    google_client_id: str | None = None
    google_client_secret: str | None = None

    meta_app_id: str | None = None
    meta_app_secret: str | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            if value.startswith("["):
                parsed = json.loads(value)
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON value must be a list")
                return [str(origin) for origin in parsed]
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        raise ValueError("CORS_ORIGINS must be a comma-separated string or list")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
