from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    Base interface for every AI provider used by CreatorOS.

    Every provider must implement the same API regardless
    of vendor (OpenAI, Gemini, Anthropic, Groq, etc.).

    Public Pipeline
        generate()
          -> chat()
          -> image()
          -> video()
          -> audio()
          -> embeddings()

    Every provider decides internally how to communicate
    with its own API while exposing a common interface.
    """

    name = "base"

    supported_asset_types: tuple[str, ...] = ()

    # ==========================================================
    # Generic Entry Point
    # ==========================================================

    async def generate(
        self,
        *,
        asset_type: str,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        if asset_type in (
            "text",
            "chat",
            "blog",
            "article",
            "script",
            "seo",
        ):
            return await self.chat(
                model=model,
                prompt=prompt,
                **kwargs,
            )

        if asset_type in (
            "image",
            "thumbnail",
            "poster",
            "logo",
            "banner",
            "cover",
            "profile_photo",
        ):
            return await self.image(
                model=model,
                prompt=prompt,
                **kwargs,
            )

        if asset_type in (
            "video",
            "short",
            "reel",
            "animation",
        ):
            return await self.video(
                model=model,
                prompt=prompt,
                **kwargs,
            )

        if asset_type in (
            "audio",
            "voice",
            "speech",
            "tts",
        ):
            return await self.audio(
                model=model,
                prompt=prompt,
                **kwargs,
            )

        raise ValueError(
            f"{self.name} does not support asset type '{asset_type}'."
        )

    # ==========================================================
    # Text
    # ==========================================================

    @abstractmethod
    async def chat(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ...

    # ==========================================================
    # Image
    # ==========================================================

    @abstractmethod
    async def image(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ...

    # ==========================================================
    # Video
    # ==========================================================

    @abstractmethod
    async def video(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ...

    # ==========================================================
    # Audio
    # ==========================================================

    @abstractmethod
    async def audio(
        self,
        *,
        model: str,
        prompt: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        ...

    # ==========================================================
    # Embeddings
    # ==========================================================

    @abstractmethod
    async def embeddings(
        self,
        text: str,
    ) -> list[float]:
        ...

    # ==========================================================
    # Health
    # ==========================================================

    @abstractmethod
    async def health_check(
        self,
    ) -> bool:
        ...

    # ==========================================================
    # Helpers
    # ==========================================================

    def not_supported(
        self,
        capability: str,
    ) -> dict[str, Any]:

        raise NotImplementedError(
            f"{self.name} does not support '{capability}'."
        )

    def response(
        self,
        *,
        model: str,
        result: Any,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        return {
            "success": True,
            "provider": self.name,
            "model": model,
            "result": result,
            "metadata": metadata or {},
        }
