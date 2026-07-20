from __future__ import annotations

import asyncio
from typing import Any

from elevenlabs.client import AsyncElevenLabs

from app.core.config import settings
from app.services.providers.base_provider import BaseProvider


class ElevenLabsProvider(BaseProvider):

    name = "elevenlabs"

    supported_asset_types = (
        "audio",
        "voice",
        "speech",
        "tts",
    )

    def __init__(self):

        self.client = AsyncElevenLabs(
            api_key=settings.ELEVENLABS_API_KEY,
        )

    # ---------------------------------------------------------

    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        return self.not_supported(
            "text generation",
        )

    # ---------------------------------------------------------

    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        return self.not_supported(
            "image generation",
        )

    # ---------------------------------------------------------

    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        return self.not_supported(
            "video generation",
        )

    # ---------------------------------------------------------

    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict:

        stream = self.client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id=model,
            text=prompt,
        )

        audio_bytes = bytearray()

        async for chunk in stream:
            audio_bytes.extend(chunk)

        return self.response(
            model=model,
            result=bytes(audio_bytes),
        )

    # ---------------------------------------------------------

    async def dub(
        self,
        *,
        source_url: str,
        target_lang: str,
        source_lang: str | None = None,
    ) -> bytes:
        """
        Dubs an existing video/audio file (given its URL) into another
        language using ElevenLabs' Dubbing API - it handles transcription,
        translation, and voice-matching on its own.
        """
        job = await self.client.dubbing.dub_a_video_or_an_audio_file(
            source_url=source_url,
            target_lang=target_lang,
            source_lang=source_lang,
            watermark=False,
        )
        dubbing_id = job.dubbing_id

        max_attempts = 120  # 120 * 5s = 10 minutes
        meta = None
        for _ in range(max_attempts):
            meta = await self.client.dubbing.get_dubbing_project_metadata(dubbing_id)
            if meta.status != "dubbing":
                break
            await asyncio.sleep(5)
        else:
            raise RuntimeError(
                f"ElevenLabs dubbing timed out after {max_attempts * 5} seconds."
            )

        if meta.status != "dubbed":
            raise RuntimeError(
                f"ElevenLabs dubbing failed (status={meta.status!r}): {meta.error}"
            )

        chunks = bytearray()
        async for chunk in self.client.dubbing.get_dubbed_file(dubbing_id, target_lang):
            chunks.extend(chunk)

        return bytes(chunks)

    # ---------------------------------------------------------

    async def embeddings(
        self,
        text: str,
    ) -> list[float]:

        raise NotImplementedError(
            "ElevenLabs embeddings not supported."
        )

    # ---------------------------------------------------------

    async def health_check(
        self,
    ) -> bool:

        return bool(
            settings.ELEVENLABS_API_KEY,
        )