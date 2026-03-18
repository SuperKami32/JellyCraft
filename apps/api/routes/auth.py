from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login() -> dict:
    return {"message": "Use Jellyfin auth bridge in next iteration."}


@router.post("/logout")
def logout() -> dict:
    return {"message": "Logged out from Jellycraft session stub."}


@router.get("/me")
def me() -> dict:
    return {"id": "demo-user", "name": "Demo User", "provider": "jellyfin"}
