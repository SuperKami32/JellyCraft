from functools import lru_cache

from apps.api.config import get_settings
from core.services.jellyfin_client import JellyfinClient


@lru_cache(maxsize=1)
def get_jellyfin_client() -> JellyfinClient:
    settings = get_settings()
    return JellyfinClient(
        base_url=settings.jellyfin_base_url,
        api_key=settings.jellyfin_api_key,
    )
