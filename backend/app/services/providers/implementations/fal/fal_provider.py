from __future__ import annotations

import os
import asyncio

import fal_client

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class FalProvider(BaseProvider):
    """
    FAL AI Provider
    """

    name = "fal"

    supported_asset_types = (
        "image",
        "thumbnail",
        "poster",
        "logo",
        "banner",
        "cover",
        "profile_photo",
    )

    async def chat(
        self,
        **kwargs,
    ):
        return self.not_supported("chat")

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs,
    ):

        # Make FAL SDK see the API key
        os.environ["FAL_KEY"] = settings.FAL_API_KEY

        def run():
            return fal_client.subscribe(
                application=model,
                arguments={
                    "prompt": prompt,
                },
            )

        result = await asyncio.to_thread(run)

        image_url = None

        if isinstance(result, dict):

            if "images" in result and result["images"]:
                image_url = result["images"][0].get("url")

            elif "image" in result:
                image_url = result["image"].get("url")

            elif "url" in result:
                image_url = result["url"]

        return self.response(
    model=model,
    result={
        "url": image_url,
    },
    metadata={
        "provider": self.name,
        "raw": str(result),   # ya repr(result)
    },
)

    async def video(
        self,
        **kwargs,
    ):
        return self.not_supported("video")

    async def audio(
        self,
        **kwargs,
    ):
        return self.not_supported("audio")

    async def embeddings(
        self,
        text: str,
    ):
        return self.not_supported("embeddings")

    async def health_check(
        self,
    ) -> bool:

        return bool(settings.FAL_API_KEY)