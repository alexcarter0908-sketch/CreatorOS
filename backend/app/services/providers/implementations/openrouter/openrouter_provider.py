from __future__ import annotations

import asyncio
from typing import Any

import requests
from openai import OpenAI

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter Provider

    Supports

    - Chat
    - Vision
    - JSON Mode
    - Function Calling
    - Image generation (via chat-completions + modalities, not the
      classic /images/generations endpoint - OpenRouter does not
      support that endpoint for third-party image models like FLUX
      or Gemini image models)

    NOTE: The SDK client is created lazily (on first real use),
    not in __init__. This means the provider can always be
    instantiated -- even with no API key configured -- and only
    fails when someone actually tries to generate something.
    This keeps provider selection/fallback/health-check logic
    crash-free regardless of which keys are configured.
    """

    name = "openrouter"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "seo",
        "script",
    )

    def __init__(self):
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:

        if self._client is None:

            if not settings.OPENROUTER_API_KEY:
                raise RuntimeError(
                    "OpenRouter API key is not configured "
                    "(OPENROUTER_API_KEY)."
                )

            self._client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
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

            temperature=kwargs.get(
                "temperature",
                0.7,
            ),

            max_tokens=kwargs.get(
                "max_tokens",
                4096,
            ),
        )

        text = response.choices[0].message.content

        return self.response(
            model=model,
            result=text,
            metadata={
                "provider": self.name,
                "usage": (
                    response.usage.model_dump()
                    if response.usage
                    else {}
                ),
            },
        )

    # ==========================================================
    # IMAGE
    # ==========================================================

    def _generate_image_sync(self, model: str, prompt: str) -> list[str]:
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError(
                "OpenRouter API key is not configured "
                "(OPENROUTER_API_KEY)."
            )

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "modalities": ["image", "text"],
            },
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        images: list[str] = []
        choices = data.get("choices", [])

        if choices:
            message = choices[0].get("message", {}) or {}
            for img in message.get("images", []) or []:
                url = (img.get("image_url") or {}).get("url")
                if url:
                    images.append(url)

        if not images:
            raise RuntimeError(
                f"OpenRouter returned no images for model '{model}'. "
                f"Raw response: {data}"
            )

        return images

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        images = await asyncio.to_thread(
            self._generate_image_sync,
            model,
            prompt,
        )

        return self.response(
            model=model,
            result=images,
            metadata={
                "provider": self.name,
            },
        )

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

        return self.not_supported(
            "video generation"
        )

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

        return self.not_supported(
            "audio generation"
        )

    # ==========================================================
    # EMBEDDINGS
    # ==========================================================

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:

        raise NotImplementedError(
            "OpenRouter embeddings are not implemented yet."
        )

    # ==========================================================
    # HEALTH
    # ==========================================================

    async def health_check(
        self,
    ) -> bool:

        if not settings.OPENROUTER_API_KEY:
            return False

        try:
            self.client.models.list()
            return True

        except Exception:
            return False