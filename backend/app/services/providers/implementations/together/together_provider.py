from __future__ import annotations

from typing import Any

from together import Together

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class TogetherProvider(BaseProvider):
    """
    Together AI Provider

    Supports:
    - Chat
    - Text Generation

    Future:
    - Image Generation
    - Embeddings

    NOTE: SDK client is created lazily (on first real use).
    """

    name = "together"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "seo",
        "script",
    )

    def __init__(self):
        self._client: Together | None = None

    @property
    def client(self) -> Together:

        if self._client is None:

            if not settings.TOGETHER_API_KEY:
                raise RuntimeError(
                    "Together API key is not configured (TOGETHER_API_KEY)."
                )

            self._client = Together(
                api_key=settings.TOGETHER_API_KEY,
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

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return self.response(
            model=model,
            result=response.choices[0].message.content,
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

        return self.not_supported("embeddings")

    # ==========================================================
    # HEALTH CHECK
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:

        if not settings.TOGETHER_API_KEY:
            return False

        try:

            self.client.models.list()

            return True

        except Exception:

            return False