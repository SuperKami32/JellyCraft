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
