from fastapi import FastAPI

from apps.api.config import get_settings
from apps.api.routes import (
    auth,
    automation,
    collections,
    dashboard,
    library,
    playback,
    recommendations,
    webhooks,
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(library.router)
app.include_router(collections.router)
app.include_router(recommendations.router)
app.include_router(playback.router)
app.include_router(automation.router)
app.include_router(webhooks.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get("/config")
def config() -> dict:
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/system/status")
def system_status() -> dict:
    return {
        "api": "online",
        "worker": "not-connected",
        "db": "in-memory",
    }
