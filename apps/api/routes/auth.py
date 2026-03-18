from fastapi import APIRouter, Depends, Header, HTTPException, status

from apps.api.deps import get_jellyfin_client
from apps.api.schemas.auth import AuthLoginRequest, AuthLoginResponse, AuthMeResponse
from core.services.jellyfin_client import JellyfinClient, JellyfinClientError

router = APIRouter(prefix="/auth", tags=["auth"])


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return token


@router.post("/login", response_model=AuthLoginResponse)
def login(payload: AuthLoginRequest, client: JellyfinClient = Depends(get_jellyfin_client)) -> AuthLoginResponse:
    try:
        auth_result = client.authenticate_user(payload.username, payload.password)
    except JellyfinClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    access_token = auth_result.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jellyfin did not return an access token")

    return AuthLoginResponse(access_token=access_token, user=auth_result["user"])


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    client: JellyfinClient = Depends(get_jellyfin_client),
) -> dict[str, str]:
    token = _bearer_token(authorization)
    try:
        client.logout(token)
    except JellyfinClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return {"message": "Logged out from Jellyfin session."}


@router.get("/me", response_model=AuthMeResponse)
def me(
    authorization: str | None = Header(default=None),
    client: JellyfinClient = Depends(get_jellyfin_client),
) -> AuthMeResponse:
    token = _bearer_token(authorization)
    try:
        user = client.get_current_user(token)
    except JellyfinClientError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return AuthMeResponse(**user)
