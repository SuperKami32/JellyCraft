from fastapi import APIRouter

from core.services.library_service import LibraryService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
library_service = LibraryService()


@router.get("/home")
def home() -> dict:
    return {
        "recently_added": library_service.recently_added(),
        "continue_watching": library_service.continue_watching(),
        "tonights_pick": library_service.tonights_pick(),
        "library_health": library_service.quality_report(),
    }


@router.get("/recently-added")
def recently_added() -> list[dict]:
    return library_service.recently_added()


@router.get("/continue-watching")
def continue_watching() -> list[dict]:
    return library_service.continue_watching()


@router.get("/tonights-pick")
def tonights_pick() -> dict:
    return library_service.tonights_pick()


@router.get("/library-health")
def library_health() -> dict:
    return library_service.quality_report()
