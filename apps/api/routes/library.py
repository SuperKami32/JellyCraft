from fastapi import APIRouter, HTTPException

from core.services.library_service import LibraryService

router = APIRouter(prefix="/library", tags=["library"])
library_service = LibraryService()


@router.get("/items")
def items() -> list[dict]:
    return library_service.list_items()


@router.get("/items/{item_id}")
def item(item_id: str) -> dict:
    found = library_service.get_item(item_id)
    if not found:
        raise HTTPException(status_code=404, detail="Media item not found")
    return found


@router.get("/duplicates")
def duplicates() -> list[dict]:
    return library_service.duplicates()


@router.get("/missing-metadata")
def missing_metadata() -> list[dict]:
    return library_service.missing_metadata()


@router.get("/quality-report")
def quality_report() -> dict:
    return library_service.quality_report()
