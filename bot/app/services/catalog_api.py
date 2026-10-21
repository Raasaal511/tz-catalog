from __future__ import annotations

import httpx

from app.config import Settings, get_settings


class CatalogApiClient:
    """HTTP client to the FastAPI catalog service. Stateless."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self.settings.internal_api_key}

    async def create_product(
        self,
        *,
        title: str,
        image_bytes: bytes,
        filename: str,
        content_type: str,
        created_by: str,
    ) -> dict:
        files = {"image": (filename, image_bytes, content_type)}
        data = {"title": title, "created_by": created_by}
        async with httpx.AsyncClient(base_url=self.settings.api_base_url, timeout=60.0) as client:
            response = await client.post(
                "/api/v1/products",
                headers=self._headers(),
                data=data,
                files=files,
            )
            response.raise_for_status()
            return response.json()


catalog_api = CatalogApiClient()
