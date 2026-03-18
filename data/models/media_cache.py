from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MediaCacheItem:
    item_id: str
    title: str
    media_type: str
    year: int | None = None
    overview: str | None = None
    has_poster: bool = False
    has_backdrop: bool = False
    genres: list[str] = field(default_factory=list)
    cast: list[str] = field(default_factory=list)
    has_subtitles: bool = False
    runtime_minutes: int | None = None
    is_duplicate: bool = False
    is_watched: bool = False
    file_path: str | None = None
