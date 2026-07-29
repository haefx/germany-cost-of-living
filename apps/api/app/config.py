"""Application configuration, sourced entirely from environment variables.

No secret ever has a real default here — ``SESSION_SECRET`` must be set
explicitly (see .env.example); everything else has a safe local-development
default.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://gcol:gcol@localhost:5432/gcol"
    session_secret: str = "insecure-development-secret-do-not-use-in-production"
    cookie_secure: bool = False
    # When web and API run on separate subdomains (e.g. app.example.com and
    # api.app.example.com), set this to their common parent domain — otherwise
    # the session cookie is host-only for the API domain and the web app's
    # auth gate never sees it. Empty means host-only, which is correct when
    # both run on the same host (localhost development, Docker Compose).
    cookie_domain: str = ""
    cors_origins: str = "http://localhost:3000"
    demo_household_ttl_hours: int = 24

    @model_validator(mode="after")
    def _secure_production_settings(self) -> Settings:
        if not self.is_production:
            return self
        if self.session_secret == "insecure-development-secret-do-not-use-in-production":
            raise ValueError("SESSION_SECRET must be explicitly set in production")
        if len(self.session_secret) < 32:
            raise ValueError("SESSION_SECRET must contain at least 32 characters in production")
        if not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
