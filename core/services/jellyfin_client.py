from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class JellyfinClientError(RuntimeError):
    pass


@dataclass(slots=True)
class JellyfinClient:
    base_url: str
    api_key: str | None = None
    timeout_seconds: float = 8.0

    def __post_init__(self) -> None:
        retries = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET", "POST"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session = requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _headers(self, token: str | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        resolved = token or self.api_key
        if resolved:
            headers["X-Emby-Token"] = resolved
        return headers

    def _request(self, method: str, path: str, token: str | None = None, **kwargs: Any) -> Any:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._headers(token=token),
                timeout=self.timeout_seconds,
                **kwargs,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise JellyfinClientError(f"Jellyfin API request failed for {path}: {exc}") from exc

        if response.content:
            return response.json()
        return None

    def authenticate_user(self, username: str, password: str) -> dict[str, Any]:
        payload = {
            "Username": username,
            "Pw": password,
        }
        data = self._request("POST", "/Users/AuthenticateByName", json=payload)
        user = data.get("User") if isinstance(data, dict) else {}
        return {
            "access_token": data.get("AccessToken"),
            "user": {
                "id": user.get("Id"),
                "name": user.get("Name"),
                "primary_image_tag": user.get("PrimaryImageTag"),
            },
        }

    def logout(self, token: str) -> None:
        self._request("POST", "/Sessions/Logout", token=token)

    def get_current_user(self, token: str) -> dict[str, Any]:
        data = self._request("GET", "/Users/Me", token=token)
        return {
            "id": data.get("Id"),
            "name": data.get("Name"),
            "primary_image_tag": data.get("PrimaryImageTag"),
        }

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
