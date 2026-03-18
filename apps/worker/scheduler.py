from __future__ import annotations

from apps.worker.tasks.duplicate_scan import run_duplicate_scan
from apps.worker.tasks.metadata_audit import run_metadata_audit
from apps.worker.tasks.recommendation_refresh import run_recommendation_refresh
from apps.worker.tasks.sync_library import run_sync_library


def run_scheduler() -> dict[str, str]:
    """Run a single-pass scheduler placeholder for local development."""

    run_sync_library()
    run_metadata_audit()
    run_duplicate_scan()
    run_recommendation_refresh()
    return {"status": "completed"}
