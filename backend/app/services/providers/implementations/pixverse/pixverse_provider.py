from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class PixVerseProvider(BaseProvider):
    """
    PixVerse Provider (real integration).

    Docs: https://docs.pixverse.ai/

    Auth: API-KEY header (PIXVERSE_API_KEY).

    Flow:
      1. POST /openapi/v2/video/text/generate -> returns video id
      2. GET  /openapi/v2/video/result/{id}    -> poll until completed
    """

    name = "pixverse"

    supported_asset_types = ("video",)

    BASE_URL = "https://app-api.pixverse.ai"

    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 120  # 10 minutes

    def _headers(self) -> dict[str, str]:

        if not settings.PIXVERSE_API_KEY:
            raise RuntimeError(
                "PixVerse API credentials are not configured "
                "(PIXVERSE_API_KEY)."
            )

        import uuid

        return {
            "API-KEY": settings.PIXVERSE_API_KEY,
            "Ai-trace-id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }

    async def _poll_task(
        self,
        client: httpx.AsyncClient,
        video_id: str,
    ) -> dict[str, Any]:

        for _ in range(self.MAX_POLL_ATTEMPTS):

            resp = await client.get(
                f"{self.BASE_URL}/openapi/v2/video/result/{video_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()

            status = (data.get("Resp") or {}).get("status")

            if status == 1:
                return data

            if status in (2, 3):
                raise RuntimeError(
                    f"PixVerse task {video_id} failed: {data}"
                )

            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

        raise RuntimeError(
            f"PixVerse task {video_id} timed out after "
            f"{self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."
        )

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
        return self.not_supported("image generation")

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        payload = {
            "prompt": prompt[:2000],
            "duration": kwargs.get("duration", 5),
            "aspect_ratio": kwargs.get("aspect_ratio", "16:9"),
            "model": kwargs.get("model") or "v3.5",
            "motion_mode": kwargs.get("motion_mode", "normal"),
            "negative_prompt": kwargs.get("negative_prompt", ""),
            "quality": kwargs.get("quality", "540p"),
            "seed": kwargs.get("seed", 0),
            "water_mark": kwargs.get("water_mark", False),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            create_resp = await client.post(
                f"{self.BASE_URL}/openapi/v2/video/text/generate",
                headers=self._headers(),
                json=payload,
            )

            if create_resp.status_code >= 400:
                raise RuntimeError(
                    f"PixVerse request failed "
                    f"({create_resp.status_code}): {create_resp.text}"
                )

            body = create_resp.json()
            video_id = (body.get("Resp") or {}).get("video_id")

            if not video_id:
                raise RuntimeError(
                    f"PixVerse did not return a video id: {create_resp.text}"
                )

            result = await self._poll_task(client, video_id)

        video_url = (result.get("Resp") or {}).get("url")

        return self.response(
            model=model,
            result={
                "urls": [video_url] if video_url else [],
            },
            metadata={
                "provider": self.name,
                "video_id": video_id,
                "raw": result,
            },
        )

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
        return bool(settings.PIXVERSE_API_KEY)




