import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    widget_session_jwt_secret: str
    widget_session_jwt_alg: str
    widget_session_ttl_minutes: int


def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    widget_session_jwt_secret = os.getenv("WIDGET_SESSION_JWT_SECRET", "")
    if not widget_session_jwt_secret:
        raise RuntimeError("WIDGET_SESSION_JWT_SECRET is not set")

    widget_session_jwt_alg = os.getenv("WIDGET_SESSION_JWT_ALG", "HS256")
    widget_session_ttl_minutes = int(os.getenv("WIDGET_SESSION_TTL_MINUTES", "10"))

    return Settings(
        database_url=database_url,
        widget_session_jwt_secret=widget_session_jwt_secret,
        widget_session_jwt_alg=widget_session_jwt_alg,
        widget_session_ttl_minutes=widget_session_ttl_minutes,
    )
