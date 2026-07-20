from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class SogniProvider(BaseProvider):
    """
    Sogni.ai Provider (real integration).

    Docs: https://docs.sogni.ai/

    Auth: Bearer token (SOGNI_API_KEY).
    Free tier: monthly Spark rendering, up to 1MP.
    """

    name = "sogni"

    supported_asset_types = ("image", "thumbnail")

    BASE_URL = "https://api.sogni.ai/v1"

    def _headers(self) -> dict[str, str]:

        if not settings.SOGNI_API_KEY:
            raise RuntimeError(
                "Sogni API credentials are not configured "
                "(SOGNI_API_KEY)."
            )

        return {
            "Authorization": f"Bearer {settings.SOGNI_API_KEY}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("text generation")

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        payload = {
            "prompt": prompt[:2000],
            "model": model or "z-image-turbo",
            "width": kwargs.get("width", 1024),
            "height": kwargs.get("height", 1024),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:

            resp = await client.post(
                f"{self.BASE_URL}/generate/image",
                headers=self._headers(),
                json=payload,
            )

            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Sogni request failed "
                    f"({resp.status_code}): {resp.text}"
                )

            data = resp.json()

        image_url = data.get("image_url") or (data.get("images") or [None])[0]

        return self.response(
            model=model,
            result={
                "urls": [image_url] if image_url else [],
            },
            metadata={
                "provider": self.name,
                "raw": data,
            },
        )

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("video generation")

    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("audio generation")

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:
        return self.not_supported("embeddings")

    async def health_check(self) -> bool:
        return bool(settings.SOGNI_API_KEY)
