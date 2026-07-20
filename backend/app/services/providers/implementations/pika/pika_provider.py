from __future__ import annotations

import os
import asyncio
from typing import Any

import fal_client

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class PikaProvider(BaseProvider):
    """
    Pika Provider (real integration).

    IMPORTANT: Pika does not run its own public API anymore.
    As of 2026, Pika's models (2.1 / 2.2) are hosted exclusively
    on fal.ai. So this provider authenticates with FAL_API_KEY,
    NOT a separate PIKA_API_KEY.

    See: https://fal.ai/models/fal-ai/pika/v2.2/text-to-video
    """

    name = "pika"

    supported_asset_types = ("video",)

    # fal.ai application id for Pika's text-to-video model.
    DEFAULT_APP = "fal-ai/pika/v2.2/text-to-video"

    # ==========================================================
    # Text — not supported
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
    # Image — not supported (Pika image-to-video is a separate
    # fal app, not wired up here)
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
    # Video — real implementation via fal.ai
    # ==========================================================

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        if not settings.FAL_API_KEY:
            raise RuntimeError(
                "Pika (via fal.ai) requires FAL_API_KEY to be configured."
            )

        # Make the fal SDK see the API key.
        os.environ["FAL_KEY"] = settings.FAL_API_KEY

        # `model` from the registry can either be the full fal
        # application id (e.g. "fal-ai/pika/v2.2/text-to-video")
        # or left blank to use the default text-to-video app.
        application = model or self.DEFAULT_APP

        arguments: dict[str, Any] = {
            "prompt": prompt,
        }

        if kwargs.get("negative_prompt"):
            arguments["negative_prompt"] = kwargs["negative_prompt"]

        if kwargs.get("seed") is not None:
            arguments["seed"] = kwargs["seed"]

        if kwargs.get("resolution"):
            arguments["resolution"] = kwargs["resolution"]

        if kwargs.get("duration"):
            arguments["duration"] = kwargs["duration"]

        def run():
            return fal_client.subscribe(
                application=application,
                arguments=arguments,
            )

        result = await asyncio.to_thread(run)

        video_url = None

        if isinstance(result, dict):
            if "video" in result and isinstance(result["video"], dict):
                video_url = result["video"].get("url")
            elif "videos" in result and result["videos"]:
                video_url = result["videos"][0].get("url")
            elif "url" in result:
                video_url = result["url"]

        return self.response(
            model=application,
            result={
                "url": video_url,
            },
            metadata={
                "provider": self.name,
                "raw": str(result),
            },
        )

    # ==========================================================
    # Audio — not supported
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
    # Embeddings — not supported
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
        return bool(settings.FAL_API_KEY)