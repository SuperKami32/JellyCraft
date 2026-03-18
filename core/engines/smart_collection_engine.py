from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CollectionRule:
    slug: str
    label: str
    min_runtime: int | None = None
    max_runtime: int | None = None
    require_unwatched: bool = True


class SmartCollectionEngine:
    """Simple rule-based collection generator for MVP workflows."""

    DEFAULT_RULES: tuple[CollectionRule, ...] = (
        CollectionRule(
            slug="best-90-120-unwatched",
            label="Best 90-120 Minute Unwatched",
            min_runtime=90,
            max_runtime=120,
            require_unwatched=True,
        ),
    )

    def available_rules(self) -> list[dict[str, str]]:
        return [{"slug": rule.slug, "label": rule.label} for rule in self.DEFAULT_RULES]

    def filter_items(self, items: list[dict], slug: str) -> list[dict]:
        rule = next((entry for entry in self.DEFAULT_RULES if entry.slug == slug), None)
        if rule is None:
            return []

        result = []
        for item in items:
            runtime = item.get("runtime_minutes")
            if runtime is None:
                continue
            if rule.min_runtime is not None and runtime < rule.min_runtime:
                continue
            if rule.max_runtime is not None and runtime > rule.max_runtime:
                continue
            if rule.require_unwatched and item.get("is_watched"):
                continue
            result.append(item)

        return sorted(result, key=lambda row: row.get("quality_score", 0), reverse=True)
