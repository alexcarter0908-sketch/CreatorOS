from __future__ import annotations

from typing import Any

from anthropic import AsyncAnthropic

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):
    """
    Anthropic Claude Provider

    Supported
    ---------
    - Chat

    Future
    ------
    - Vision

    NOTE: SDK client is created lazily (on first real use).
    """

    name = "anthropic"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "seo",
        "script",
    )

    def __init__(self):
        self._client: AsyncAnthropic | None = None

    @property
    def client(self) -> AsyncAnthropic:

        if self._client is None:

            if not settings.ANTHROPIC_API_KEY:
                raise RuntimeError(
                    "Anthropic API key is not configured (ANTHROPIC_API_KEY)."
                )

            self._client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
            )

        return self._client

    # ======================================================
    # CHAT
    # ======================================================

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        response = await self.client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return self.response(
            model=model,
            result=response.content[0].text,
            metadata={
                "provider": self.name,
                "usage": getattr(response, "usage", None),
            },
        )

    # ======================================================
    # IMAGE
    # ======================================================

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.not_supported("image generation")

    # ======================================================
    # VIDEO
    # ======================================================

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.not_supported("video generation")

    # ======================================================
    # AUDIO
    # ======================================================

    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        return self.not_supported("audio generation")

    # ======================================================
    # EMBEDDINGS
    # ======================================================

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:

        return self.not_supported("embeddings")

    # ======================================================
    # HEALTH
    # ======================================================

    async def health_check(self) -> bool:

        if not settings.ANTHROPIC_API_KEY:
            return False

        try:

            await self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1,
                messages=[
                    {
                        "role": "user",
                        "content": "ping",
                    }
                ],
            )

            return True

        except Exception:

            return False