import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_home_shape() -> None:
    response = client.get("/dashboard/home")
    assert response.status_code == 200
    payload = response.json()
    assert "recently_added" in payload
    assert "continue_watching" in payload
    assert "tonights_pick" in payload
    assert "library_health" in payload


def test_library_item_by_id() -> None:
    response = client.get("/library/items/movie-001")
    assert response.status_code == 200
    assert response.json()["item_id"] == "movie-001"


def test_library_item_not_found() -> None:
    response = client.get("/library/items/does-not-exist")
    assert response.status_code == 404


def test_collection_generate_endpoint() -> None:
    response = client.post("/collections/generate")
    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == "best-90-120-unwatched"
    assert isinstance(payload["items"], list)


def test_recommendations_and_explain_endpoints() -> None:
    response = client.get("/recommendations/me")
    assert response.status_code == 200
    assert "items" in response.json()

    explain_response = client.get("/recommendations/explain/movie-003")
    assert explain_response.status_code == 200
    assert explain_response.json()["item_id"] == "movie-003"


def test_automation_and_webhook_endpoints() -> None:
    automation_response = client.post("/automation/refresh-library")
    assert automation_response.status_code == 200
    assert automation_response.json()["status"] == "queued"

    webhook_response = client.post("/webhooks/jellyfin", json={"type": "media.added"})
    assert webhook_response.status_code == 200
    assert webhook_response.json()["event_type"] == "media.added"
