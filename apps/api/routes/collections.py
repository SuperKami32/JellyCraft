from fastapi import APIRouter

from core.services.library_service import LibraryService

router = APIRouter(prefix="/collections", tags=["collections"])
library_service = LibraryService()


@router.get("")
def list_collections() -> list[dict[str, str]]:
    return library_service.collection_rules()


@router.post("/generate")
def generate_collection(slug: str = "best-90-120-unwatched") -> dict:
    return library_service.generate_collection(slug)


@router.post("/refresh/{slug}")
def refresh_collection(slug: str) -> dict:
    return {
        "slug": slug,
        "status": "queued",
        "message": "Collection refresh task queued.",
    }
