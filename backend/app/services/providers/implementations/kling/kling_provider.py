from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
import jwt  # pip install pyjwt --break-system-packages

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class KlingProvider(BaseProvider):
    """
    Kling AI Provider (real integration).

    Docs: https://app.klingai.com/global/dev/document-api

    Auth: Kling does NOT use a plain API key. You authenticate
    with a short-lived JWT built from an AccessKey + SecretKey
    pair (settings.KLING_ACCESS_KEY / settings.KLING_SECRET_KEY).

    Flow:
      1. POST /v1/videos/text2video          -> returns a task_id
      2. GET  /v1/videos/text2video/{task_id} -> poll until succeed/failed
    """

    name = "kling"

    supported_asset_types = ("video",)

    BASE_URL = "https://api-singapore.klingai.com/v1"

    TOKEN_TTL_SECONDS = 1800  # Kling tokens expire after 30 minutes
    POLL_INTERVAL_SECONDS = 5
    MAX_POLL_ATTEMPTS = 120  # 120 * 5s = 10 minutes

    # ==========================================================
    # JWT auth
    # ==========================================================

    def _generate_token(self) -> str:

        if not settings.KLING_ACCESS_KEY or not settings.KLING_SECRET_KEY:
            raise RuntimeError(
                "Kling API credentials are not configured "
                "(KLING_ACCESS_KEY / KLING_SECRET_KEY)."
            )

        now = int(time.time())

        payload = {
            "iss": settings.KLING_ACCESS_KEY,
            "exp": now + self.TOKEN_TTL_SECONDS,
            "nbf": now - 5,
        }

        token = jwt.encode(
            payload,
            settings.KLING_SECRET_KEY,
            algorithm="HS256",
            headers={"typ": "JWT"},
        )

        if isinstance(token, bytes):
            token = token.decode("utf-8")

        return token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._generate_token()}",
            "Content-Type": "application/json",
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
                f"{self.BASE_URL}/videos/text2video/{task_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            body = resp.json()
            data = body.get("data", {})

            status = data.get("task_status")

            if status == "succeed":
                return data

            if status == "failed":
                raise RuntimeError(
                    f"Kling task {task_id} failed: "
                    f"{data.get('task_status_msg', 'unknown error')}"
                )

            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

        raise RuntimeError(
            f"Kling task {task_id} timed out after "
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
    # Image - not supported (Kling has image endpoints, not
    # wired up in this provider)
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

        payload: dict[str, Any] = {
            "model_name": model,
            "prompt": prompt,
            "duration": str(kwargs.get("duration", 5)),
            "mode": kwargs.get("mode", "std"),
            "aspect_ratio": kwargs.get("ratio", "16:9"),
        }

        if kwargs.get("negative_prompt"):
            payload["negative_prompt"] = kwargs["negative_prompt"]

        async with httpx.AsyncClient(timeout=30.0) as client:

            create_resp = await client.post(
                f"{self.BASE_URL}/videos/text2video",
                headers=self._headers(),
                json=payload,
            )

            if create_resp.status_code >= 400:
                raise RuntimeError(
                    f"Kling request failed "
                    f"({create_resp.status_code}): {create_resp.text}"
                )

            body = create_resp.json()
            task_id = body.get("data", {}).get("task_id")

            if not task_id:
                raise RuntimeError(
                    f"Kling did not return a task id: {create_resp.text}"
                )

            result = await self._poll_task(client, task_id)

        videos = result.get("task_result", {}).get("videos", [])
        video_url = videos[0].get("url") if videos else None

        return self.response(
            model=model,
            result={
                "url": video_url,
                "urls": [v.get("url") for v in videos],
            },
            metadata={
                "provider": self.name,
                "task_id": task_id,
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
        return bool(
            settings.KLING_ACCESS_KEY and settings.KLING_SECRET_KEY
        )
