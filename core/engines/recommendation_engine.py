from __future__ import annotations


class RecommendationEngine:
    """Heuristic recommendation engine for Phase 1/2."""

    def recommend_for_user(self, items: list[dict], user_id: str, limit: int = 5) -> list[dict]:
        _ = user_id
        candidates = [
            item
            for item in items
            if not item.get("is_watched") and item.get("quality_score", 0) >= 60
        ]
        ranked = sorted(
            candidates,
            key=lambda entry: (
                entry.get("quality_score", 0),
                bool(entry.get("has_subtitles")),
                bool(entry.get("overview")),
            ),
            reverse=True,
        )
        return ranked[:limit]

    def explain(self, item: dict) -> list[str]:
        reasons = []
        if item.get("quality_score", 0) >= 75:
            reasons.append("High metadata quality and likely polished file")
        if item.get("runtime_minutes") and 90 <= item["runtime_minutes"] <= 125:
            reasons.append("Runtime aligns with a typical evening watch")
        if item.get("genres"):
            reasons.append(f"Genre match candidate: {', '.join(item['genres'][:2])}")

        return reasons or ["Fallback recommendation based on available library signals"]
