from fastapi import APIRouter

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/jellyfin")
def jellyfin_webhook(event: dict) -> dict:
    event_type = event.get("type", "unknown")
    return {"status": "accepted", "event_type": event_type}


@router.post("/test")
def test_webhook(payload: dict) -> dict:
    return {"status": "ok", "payload": payload}
