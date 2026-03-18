from fastapi import APIRouter

from core.services.library_service import LibraryService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
library_service = LibraryService()


@router.get("/me")
def recommendations_me(user_id: str = "demo-user") -> dict:
    return {
        "user_id": user_id,
        "items": library_service.recommendations_for_user(user_id),
    }


@router.get("/explain/{media_id}")
def explain(media_id: str) -> dict:
    return library_service.recommendation_explanation(media_id)


@router.post("/rebuild")
def rebuild() -> dict:
    return {
        "status": "queued",
        "message": "Recommendation rebuild queued.",
    }
