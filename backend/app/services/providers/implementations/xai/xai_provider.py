from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class XAIProvider(BaseProvider):
    """
    xAI (Grok) Provider
    OpenAI-compatible implementation.

    NOTE: The SDK client is created lazily (on first real use),
    not in __init__. This means the provider can always be
    instantiated -- even with no API key configured -- and only
    fails when someone actually tries to generate something.
    """

    name = "xai"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "script",
        "seo",
    )

    def __init__(self):
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:

        if self._client is None:

            if not settings.XAI_API_KEY:
                raise RuntimeError(
                    "xAI API key is not configured (XAI_API_KEY)."
                )

            self._client = OpenAI(
                api_key=settings.XAI_API_KEY,
                base_url="https://api.x.ai/v1",
            )

        return self._client

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
            temperature=kwargs.get(
                "temperature",
                0.7,
            ),
            max_tokens=kwargs.get(
                "max_tokens",
                2048,
            ),
        )

        return self.response(
            model=model,
            result=response.choices[0].message.content,
            metadata={
                "finish_reason": response.choices[0].finish_reason,
            },
        )

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("image")

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("video")

    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("audio")

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:
        return self.not_supported("embeddings")

    async def health_check(
        self,
    ) -> bool:

        if not settings.XAI_API_KEY:
            return False

        try:
            self.client.chat.completions.create(
                model="grok-4",
                messages=[
                    {
                        "role": "user",
                        "content": "ping",
                    }
                ],
                max_tokens=1,
            )
            return True

        except Exception:
            return False