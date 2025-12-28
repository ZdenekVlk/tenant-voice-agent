import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str


def get_settings() -> Settings:
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return Settings(database_url=database_url)
