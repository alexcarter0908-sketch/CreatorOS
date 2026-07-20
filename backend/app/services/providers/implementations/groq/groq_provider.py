from __future__ import annotations

from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


_shared_groq_client: AsyncOpenAI | None = None


class GroqProvider(BaseProvider):
    """
    Groq Provider

    NOTE: SDK client is created lazily (on first real use) and then
    reused across every GroqProvider instance/request, so we are not
    opening a brand new HTTPS connection to Groq on every single chat
    message. The response content and behavior are unchanged - this
    only removes repeated connection setup overhead.
    """

    name = "groq"

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

        global _shared_groq_client

        if _shared_groq_client is None:

            if not settings.GROQ_API_KEY:
                raise RuntimeError(
                    "Groq API key is not configured (GROQ_API_KEY)."
                )

            _shared_groq_client = AsyncOpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )

        return _shared_groq_client

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=kwargs.get("temperature", 0.7),
        )

        return self.response(
            model=model,
            result=response.choices[0].message.content,
            metadata={
                "provider": self.name,
                "usage": response.usage.model_dump() if response.usage else None,
            },
        )

    async def stream_chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Token-by-token streaming chat, used by the /commands/run/stream
        endpoint for a fast "typing" effect. Not part of the BaseProvider
        interface -- called directly, since streaming has a fundamentally
        different return shape (generator vs dict) than every other
        provider method.
        """

        stream = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=kwargs.get("temperature", 0.7),
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

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

        return self.not_supported("video generation")

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

    async def health_check(
        self,
    ) -> bool:

        if not settings.GROQ_API_KEY:
            return False

        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
