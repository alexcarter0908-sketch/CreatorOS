from __future__ import annotations

from typing import Any

from google import genai

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):
    """
    Google Gemini Provider

    Supported
    ---------
    - Chat
    - Vision (future)

    Future
    ------
    - Images
    - Audio
    - Video

    NOTE: SDK client is created lazily (on first real use).
    """

    name = "gemini"

    supported_asset_types = (
        "text",
        "chat",
        "blog",
        "article",
        "seo",
        "script",
    )

    def __init__(self):
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:

        if self._client is None:

            if not settings.GEMINI_API_KEY:
                raise RuntimeError(
                    "Gemini API key is not configured (GEMINI_API_KEY)."
                )

            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
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

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return self.response(
            model=model,
            result=response.text,
            metadata={
                "provider": self.name,
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

        if not settings.GEMINI_API_KEY:
            return False

        try:

            self.client.models.list()

            return True

        except Exception:

            return False