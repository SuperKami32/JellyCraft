from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DatabaseConfig:
    url: str = "sqlite:///./jellycraft.db"


def get_database_config() -> DatabaseConfig:
    """Return current DB configuration placeholder.

    This keeps DB concerns explicit until SQLAlchemy integration lands.
    """

    return DatabaseConfig()
