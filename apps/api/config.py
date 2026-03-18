from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Jellycraft API"
    app_version: str = "0.1.0"
    environment: str = "development"
    jellyfin_base_url: str = "http://localhost:8096"
    jellyfin_api_key: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
