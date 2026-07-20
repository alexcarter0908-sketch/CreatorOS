from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class FishAudioProvider(BaseProvider):
    """
    Fish Audio Provider (real integration).

    Docs: https://docs.fish.audio/

    Auth: Bearer token (FISH_AUDIO_API_KEY).
    Free tier model: s2.1-pro-free
    """

    name = "fish_audio"

    supported_asset_types = ("audio", "voice", "speech", "tts")

    BASE_URL = "https://api.fish.audio/v1"

    def _headers(self) -> dict[str, str]:

        if not settings.FISH_AUDIO_API_KEY:
            raise RuntimeError(
                "Fish Audio API credentials are not configured "
                "(FISH_AUDIO_API_KEY)."
            )

        return {
            "Authorization": f"Bearer {settings.FISH_AUDIO_API_KEY}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return self.not_supported("text generation")

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

        payload = {
            "text": prompt,
            "model": model or "s2.1-pro-free",
            "format": kwargs.get("format", "mp3"),
        }

        async with httpx.AsyncClient(timeout=60.0) as client:

            resp = await client.post(
                f"{self.BASE_URL}/tts",
                headers=self._headers(),
                json=payload,
            )

            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Fish Audio request failed "
                    f"({resp.status_code}): {resp.text}"
                )

            audio_bytes = resp.content

        return self.response(
            model=model,
            result=audio_bytes,
            metadata={
                "provider": self.name,
            },
        )

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:
        return self.not_supported("embeddings")

    async def health_check(self) -> bool:
        return bool(settings.FISH_AUDIO_API_KEY)
