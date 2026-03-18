from fastapi import APIRouter

router = APIRouter(prefix="/automation", tags=["automation"])


def _queued(task_name: str) -> dict:
    return {"task": task_name, "status": "queued"}


@router.post("/refresh-library")
def refresh_library() -> dict:
    return _queued("refresh-library")


@router.post("/refresh-metadata")
def refresh_metadata() -> dict:
    return _queued("refresh-metadata")


@router.post("/fetch-subtitles")
def fetch_subtitles() -> dict:
    return _queued("fetch-subtitles")


@router.post("/run-quality-scan")
def run_quality_scan() -> dict:
    return _queued("run-quality-scan")
