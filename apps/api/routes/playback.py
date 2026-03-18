from fastapi import APIRouter

from core.services.library_service import LibraryService

router = APIRouter(prefix="/playback", tags=["playback"])
library_service = LibraryService()


@router.get("/in-progress")
def in_progress() -> list[dict]:
    return library_service.in_progress()


@router.get("/history")
def history() -> list[dict]:
    return library_service.history()


@router.post("/pick-tonight")
def pick_tonight() -> dict:
    return library_service.tonights_pick()
