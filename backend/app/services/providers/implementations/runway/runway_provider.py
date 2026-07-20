from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class RunwayProvider(BaseProvider):
    """
    Runway ML Provider (real integration).

    Docs: https://docs.dev.runwayml.com/

    Auth: Bearer token (RUNWAY_API_KEY) plus a required API
    version header.

    Flow:
      1. POST /v1/text_to_video (or /v1/image_to_video) -> returns task id
      2. GET  /v1/tasks/{id}                              -> poll until
                                                              SUCCEEDED/FAILED
    """

    name = "runway"

    supported_asset_types = ("video",)

    BASE_URL = "https://api.dev.runwayml.com/v1"

    API_VERSION = "2024-11-06"

    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 120  # 120 * 5s = 10 minutes

    # ==========================================================
    # Auth headers
    # ==========================================================

    def _headers(self) -> dict[str, str]:

        if not settings.RUNWAY_API_KEY:
            raise RuntimeError(
                "Runway API credentials are not configured "
                "(RUNWAY_API_KEY)."
            )

        return {
            "Authorization": f"Bearer {settings.RUNWAY_API_KEY}",
            "Content-Type": "application/json",
            "X-Runway-Version": self.API_VERSION,
        }

    # ==========================================================
    # Polling
    # ==========================================================

    async def _poll_task(
        self,
        client: httpx.AsyncClient,
        task_id: str,
    ) -> dict[str, Any]:

        for _ in range(self.MAX_POLL_ATTEMPTS):

            resp = await client.get(
                f"{self.BASE_URL}/tasks/{task_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()

            status = data.get("status")

            if status == "SUCCEEDED":
                return data

            if status in ("FAILED", "CANCELLED"):
                raise RuntimeError(
                    f"Runway task {task_id} {status.lower()}: "
                    f"{data.get('failure', 'unknown error')}"
                )

            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

        raise RuntimeError(
            f"Runway task {task_id} timed out after "
            f"{self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL_SECONDS} seconds."
        )

    # ==========================================================
    # Text - not supported
    # ==========================================================

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("text generation")

    # ==========================================================
    # Image - not supported (Runway has text_to_image endpoints,
    # not wired up in this provider)
    # ==========================================================

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("image generation")

    # ==========================================================
    # Video - real implementation
    # ==========================================================

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        image_url = kwargs.get("image_url")

        payload: dict[str, Any] = {
            "model": model or "gen4_turbo",
            "promptText": prompt[:800],
            "ratio": kwargs.get("ratio", "1280:720"),
            "duration": kwargs.get("duration", 5),
        }

        if kwargs.get("seed") is not None:
            payload["seed"] = kwargs["seed"]

        if image_url:
            endpoint = "image_to_video"
            payload["promptImage"] = image_url
        else:
            endpoint = "text_to_video"

        async with httpx.AsyncClient(timeout=30.0) as client:

            create_resp = await client.post(
                f"{self.BASE_URL}/{endpoint}",
                headers=self._headers(),
                json=payload,
            )

            if create_resp.status_code >= 400:
                raise RuntimeError(
                    f"Runway request failed "
                    f"({create_resp.status_code}): {create_resp.text}"
                )

            body = create_resp.json()
            task_id = body.get("id")

            if not task_id:
                raise RuntimeError(
                    f"Runway did not return a task id: {create_resp.text}"
                )

            result = await self._poll_task(client, task_id)

        output = result.get("output", [])
        video_url = output[0] if output else None

        return self.response(
            model=model,
            result={
                "url": video_url,
                "urls": output,
            },
            metadata={
                "provider": self.name,
                "task_id": task_id,
                "endpoint": endpoint,
                "raw": result,
            },
        )

    # ==========================================================
    # Audio - not supported
    # ==========================================================

    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("audio generation")

    # ==========================================================
    # Embeddings - not supported
    # ==========================================================

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:
        return self.not_supported("embeddings")

    # ==========================================================
    # Health
    # ==========================================================

    async def health_check(self) -> bool:
        return bool(settings.RUNWAY_API_KEY)


