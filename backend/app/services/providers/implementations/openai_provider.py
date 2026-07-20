from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI Provider

    Supported
    ---------
    - Chat
    - Embeddings

    Future
    ------
    - Images
    - Audio
    - Video

    NOTE: The SDK client is created lazily (on first real use),
    not in __init__. This means the provider can always be
    instantiated -- even with no API key configured -- and only
    fails when someone actually tries to generate something.
    """

    name = "openai"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "seo",
        "script",
    )

    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:

        if self._client is None:

            if not settings.OPENAI_API_KEY:
                raise RuntimeError(
                    "OpenAI API key is not configured (OPENAI_API_KEY)."
                )

            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
            )

        return self._client

    # ==========================================================
    # CHAT
    # ==========================================================

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        response = await self.client.responses.create(
            model=model,
            input=prompt,
        )

        return self.response(
            model=model,
            result=response.output_text,
            metadata={
                "provider": self.name,
            },
        )

    # ==========================================================
    # IMAGE
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
    # VIDEO
    # ==========================================================

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.not_supported("video generation")

    # ==========================================================
    # AUDIO
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
    # EMBEDDINGS
    # ==========================================================

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:

        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )

        return response.data[0].embedding

    # ==========================================================
    # HEALTH
    # ==========================================================

    async def health_check(self) -> bool:

        if not settings.OPENAI_API_KEY:
            return False

        try:

            await self.client.models.list()

            return True

        except Exception:

            return False