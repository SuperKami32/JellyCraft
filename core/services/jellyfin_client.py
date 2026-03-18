from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class JellyfinClientError(RuntimeError):
    pass


@dataclass(slots=True)
class JellyfinClient:
    base_url: str
    api_key: str | None = None
    timeout_seconds: float = 8.0

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Emby-Token"] = self.api_key
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(),
                timeout=self.timeout_seconds,
                **kwargs,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise JellyfinClientError(f"Jellyfin API request failed for {path}: {exc}") from exc

        if response.content:
            return response.json()
        return None

    def get_system_info(self) -> dict[str, Any]:
        data = self._request("GET", "/System/Info/Public")
        return {
            "server_name": data.get("ServerName"),
            "version": data.get("Version"),
            "product_name": data.get("ProductName"),
            "startup_wizard_completed": data.get("StartupWizardCompleted"),
        }

    def get_user_views(self, user_id: str) -> list[dict[str, Any]]:
        data = self._request("GET", f"/Users/{user_id}/Views")
        items = data.get("Items", []) if isinstance(data, dict) else []
        return [
            {
                "id": view.get("Id"),
                "name": view.get("Name"),
                "collection_type": view.get("CollectionType"),
            }
            for view in items
        ]

    def get_recent_items(self, user_id: str, limit: int = 15) -> list[dict[str, Any]]:
        data = self._request(
            "GET",
            f"/Users/{user_id}/Items/Latest",
            params={"Limit": limit},
        )
        if not isinstance(data, list):
            return []

        return [
            {
                "id": item.get("Id"),
                "title": item.get("Name"),
                "type": item.get("Type"),
                "year": item.get("ProductionYear"),
            }
            for item in data
        ]
