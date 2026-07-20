from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class MistralProvider(BaseProvider):
    """
    Mistral AI Provider

    Mistral's "La Plateforme" API is OpenAI-compatible, so we
    reuse the OpenAI SDK pointed at Mistral's base URL (same
    pattern as DeepSeek, Groq, xAI).

    NOTE: SDK client is created lazily (on first real use).
    """

    name = "mistral"

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

            if not settings.MISTRAL_API_KEY:
                raise RuntimeError(
                    "Mistral API key is not configured (MISTRAL_API_KEY)."
                )

            self._client = OpenAI(
                api_key=settings.MISTRAL_API_KEY,
                base_url="https://api.mistral.ai/v1",
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
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2048),
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

        if not settings.MISTRAL_API_KEY:
            return self.not_supported("embeddings")

        response = self.client.embeddings.create(
            model="mistral-embed",
            input=text,
        )

        return response.data[0].embedding

    async def health_check(
        self,
    ) -> bool:

        if not settings.MISTRAL_API_KEY:
            return False

        try:
            self.client.chat.completions.create(
                model="mistral-small-latest",
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