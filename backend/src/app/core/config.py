import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    widget_session_jwt_secret: str
    widget_session_jwt_alg: str
    widget_session_ttl_minutes: int
    rate_limit_session_tenant: str
    rate_limit_messages_tenant: str
    rate_limit_session_ip: str
    rate_limit_messages_ip: str
    max_json_body_bytes: int
    max_message_text_len: int


def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    widget_session_jwt_secret = os.getenv("WIDGET_SESSION_JWT_SECRET", "")
    if not widget_session_jwt_secret:
        raise RuntimeError("WIDGET_SESSION_JWT_SECRET is not set")

    widget_session_jwt_alg = os.getenv("WIDGET_SESSION_JWT_ALG", "HS256")
    widget_session_ttl_minutes = int(os.getenv("WIDGET_SESSION_TTL_MINUTES", "10"))
    rate_limit_session_tenant = os.getenv("RATE_LIMIT_SESSION_TENANT", "30/min")
    rate_limit_messages_tenant = os.getenv("RATE_LIMIT_MESSAGES_TENANT", "120/min")
    rate_limit_session_ip = os.getenv("RATE_LIMIT_SESSION_IP", "20/min")
    rate_limit_messages_ip = os.getenv("RATE_LIMIT_MESSAGES_IP", "60/min")
    max_json_body_bytes = int(os.getenv("MAX_JSON_BODY_BYTES", "65536"))
    max_message_text_len = int(os.getenv("MAX_MESSAGE_TEXT_LEN", "2000"))

    return Settings(
        database_url=database_url,
        widget_session_jwt_secret=widget_session_jwt_secret,
        widget_session_jwt_alg=widget_session_jwt_alg,
        widget_session_ttl_minutes=widget_session_ttl_minutes,
        rate_limit_session_tenant=rate_limit_session_tenant,
        rate_limit_messages_tenant=rate_limit_messages_tenant,
        rate_limit_session_ip=rate_limit_session_ip,
        rate_limit_messages_ip=rate_limit_messages_ip,
        max_json_body_bytes=max_json_body_bytes,
        max_message_text_len=max_message_text_len,
    )
