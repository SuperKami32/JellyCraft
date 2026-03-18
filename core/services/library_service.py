from __future__ import annotations

from dataclasses import asdict

from core.engines.metadata_score_engine import MetadataScoreEngine, MetadataSignals
from data.models.media_cache import MediaCacheItem


class LibraryService:
    """Read-model style library intelligence service."""

    def __init__(self) -> None:
        self._scorer = MetadataScoreEngine()
        self._items: list[MediaCacheItem] = [
            MediaCacheItem(
                item_id="movie-001",
                title="The Matrix",
                media_type="Movie",
                year=1999,
                overview="A computer hacker learns reality is a simulation.",
                has_poster=True,
                has_backdrop=True,
                genres=["Action", "Sci-Fi"],
                cast=["Keanu Reeves"],
                has_subtitles=True,
                runtime_minutes=136,
                file_path="/media/movies/The.Matrix.1999.mkv",
            ),
            MediaCacheItem(
                item_id="movie-002",
                title="Unlabeled Rip",
                media_type="Movie",
                has_poster=False,
                has_backdrop=False,
                has_subtitles=False,
                file_path="/media/movies/MOV_001_FINAL2.mkv",
            ),
            MediaCacheItem(
                item_id="movie-003",
                title="Blade Runner",
                media_type="Movie",
                year=1982,
                overview="A blade runner hunts rogue replicants.",
                has_poster=True,
                genres=["Sci-Fi"],
                has_subtitles=True,
                runtime_minutes=117,
                is_duplicate=True,
                file_path="/media/movies/Blade.Runner.Directors.Cut.mkv",
            ),
        ]

    def _quality_score_for(self, item: MediaCacheItem) -> int:
        signals = MetadataSignals(
            has_title=bool(item.title),
            has_year=item.year is not None,
            has_overview=bool(item.overview),
            has_poster=item.has_poster,
            has_backdrop=item.has_backdrop,
            has_genres=bool(item.genres),
            has_cast=bool(item.cast),
            has_subtitles=item.has_subtitles,
            has_runtime=item.runtime_minutes is not None,
            duplicate_suspected=item.is_duplicate,
            bad_filename=(item.file_path or "").lower().startswith("/media/movies/mov"),
        )
        return self._scorer.score(signals)

    def list_items(self) -> list[dict]:
        return [
            {
                **asdict(item),
                "quality_score": self._quality_score_for(item),
            }
            for item in self._items
        ]

    def get_item(self, item_id: str) -> dict | None:
        for item in self._items:
            if item.item_id == item_id:
                return {**asdict(item), "quality_score": self._quality_score_for(item)}
        return None

    def duplicates(self) -> list[dict]:
        return [item for item in self.list_items() if item["is_duplicate"]]

    def missing_metadata(self) -> list[dict]:
        def has_missing(item: dict) -> bool:
            return not item["has_poster"] or not item["overview"] or not item["has_subtitles"]

        return [item for item in self.list_items() if has_missing(item)]

    def quality_report(self) -> dict:
        items = self.list_items()
        if not items:
            return {"average_score": 0, "weak_items": [], "total_items": 0}

        average = round(sum(item["quality_score"] for item in items) / len(items), 2)
        weak_items = [item for item in items if item["quality_score"] < 60]
        return {
            "average_score": average,
            "weak_items": weak_items,
            "total_items": len(items),
        }

    def continue_watching(self) -> list[dict]:
        return [
            {
                "item_id": "movie-001",
                "title": "The Matrix",
                "progress_percent": 43,
                "remaining_minutes": 78,
            }
        ]

    def recently_added(self) -> list[dict]:
        return [
            {
                "item_id": item.item_id,
                "title": item.title,
                "year": item.year,
                "media_type": item.media_type,
            }
            for item in self._items[:6]
        ]

    def tonights_pick(self) -> dict:
        candidates = [
            item
            for item in self.list_items()
            if item["runtime_minutes"] and 90 <= item["runtime_minutes"] <= 120
        ]
        if not candidates:
            return {"reason": "No 90-120 minute candidates available yet."}

        best = max(candidates, key=lambda item: item["quality_score"])
        return {
            "item_id": best["item_id"],
            "title": best["title"],
            "reason": "High-quality unwatched runtime fit.",
        }
