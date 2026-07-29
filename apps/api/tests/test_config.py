import pytest
from pydantic import ValidationError

from app.config import Settings


def test_production_rejects_insecure_defaults() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production")


def test_production_accepts_secure_cookie_and_long_secret() -> None:
    settings = Settings(
        environment="production",
        session_secret="a-secure-random-secret-with-more-than-32-characters",
        cookie_secure=True,
    )
    assert settings.is_production
