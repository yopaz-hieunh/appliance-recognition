
from __future__ import annotations

import json
from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, SecretStr, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings.

    Loads values from environment variables and a local `.env` file (if present).

    Notes:
    - This example uses the Pydantic v1-style `BaseSettings`. If your project
      uses Pydantic v2 / pydantic-settings, adapt accordingly.
    """

    # App
    APP_NAME: str = "Appliance Recognition"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "An application to recognize appliances in images."
    APP_ENV: str = Field("development", description="Application environment")
    DEBUG: bool = Field(True, description="Enable debug/auto-reload features")
    PORT: int = Field(8000, description="Port to run the application on")

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # one week

    # Database
    DATABASE_URL: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Optional external services
    SENTRY_DSN: Optional[AnyHttpUrl] = None
    REDIS_URL: Optional[str] = None

    # Logging
    LOG_LEVEL: str = Field("INFO", description="Default log level")
    GOOGLE_API_KEY: str
    # API
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    UPLOAD_FOLDER: str = "upload"

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins for development."""
        if self.DEBUG:
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ]
        return []

    @property
    def sqlalchemy_database_uri(self) -> Optional[str]:
        """Compatibility helper used by many libraries expecting SQLAlchemy URL.

        Returns the configured `DATABASE_URL` unchanged (if present). You may
        extend this to construct the URL from separate parts.
        """
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Use this function throughout the codebase (for example in dependencies)
    to avoid reloading environment variables multiple times.
    """
    return Settings()


# Example usage:
# from app.core.config import get_settings
# settings = get_settings()
# print(settings.DATABASE_URL)
