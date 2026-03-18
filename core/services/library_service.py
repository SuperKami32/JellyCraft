from __future__ import annotations

from dataclasses import asdict

from core.engines.metadata_score_engine import MetadataScoreEngine, MetadataSignals
from core.engines.recommendation_engine import RecommendationEngine
from core.engines.smart_collection_engine import SmartCollectionEngine
from data.models.media_cache import MediaCacheItem


class LibraryService:
    """Read-model style library intelligence service."""

    def __init__(self) -> None:
        self._scorer = MetadataScoreEngine()
        self._collection_engine = SmartCollectionEngine()
        self._recommendation_engine = RecommendationEngine()
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
                is_watched=False,
                file_path="/media/movies/The.Matrix.1999.mkv",
            ),
            MediaCacheItem(
                item_id="movie-002",
                title="Unlabeled Rip",
                media_type="Movie",
                has_poster=False,
                has_backdrop=False,
                has_subtitles=False,
                is_watched=False,
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
                is_watched=False,
                file_path="/media/movies/Blade.Runner.Directors.Cut.mkv",
            ),
            MediaCacheItem(
                item_id="movie-004",
                title="Arrival",
                media_type="Movie",
                year=2016,
                overview="A linguist works to communicate with alien visitors.",
                has_poster=True,
                has_backdrop=True,
                genres=["Sci-Fi", "Drama"],
                cast=["Amy Adams"],
                has_subtitles=True,
                runtime_minutes=116,
                is_watched=True,
                file_path="/media/movies/Arrival.2016.mkv",
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
        candidates = self._collection_engine.filter_items(self.list_items(), "best-90-120-unwatched")
        if not candidates:
            return {"reason": "No 90-120 minute candidates available yet."}

        best = candidates[0]
        return {
            "item_id": best["item_id"],
            "title": best["title"],
            "reason": "High-quality unwatched runtime fit.",
        }

    def in_progress(self) -> list[dict]:
        return self.continue_watching()

    def history(self) -> list[dict]:
        watched = [item for item in self.list_items() if item["is_watched"]]
        return [{"item_id": item["item_id"], "title": item["title"], "finished": True} for item in watched]

    def recommendations_for_user(self, user_id: str) -> list[dict]:
        return self._recommendation_engine.recommend_for_user(self.list_items(), user_id)

    def recommendation_explanation(self, item_id: str) -> dict:
        item = self.get_item(item_id)
        if not item:
            return {"item_id": item_id, "reasons": ["Item not found"]}
        return {"item_id": item_id, "reasons": self._recommendation_engine.explain(item)}

    def collection_rules(self) -> list[dict[str, str]]:
        return self._collection_engine.available_rules()

    def generate_collection(self, slug: str) -> dict:
        items = self._collection_engine.filter_items(self.list_items(), slug)
        return {
            "slug": slug,
            "count": len(items),
            "items": [{"item_id": item["item_id"], "title": item["title"]} for item in items],
        }
