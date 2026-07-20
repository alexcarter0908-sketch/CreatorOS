from __future__ import annotations

from typing import Any

import replicate

from app.core.config.settings import settings
from app.services.providers.base_provider import BaseProvider


class ReplicateProvider(BaseProvider):
    """
    Replicate Provider

    Supported
    ---------
    - Image Generation
    - Video Generation

    NOTE: SDK client is created lazily (on first real use).
    """

    name = "replicate"

    supported_asset_types = (
        "image",
        "thumbnail",
        "poster",
        "logo",
        "banner",
        "cover",
        "profile_photo",
    )

    def __init__(self):
        self._client: replicate.Client | None = None

    @property
    def client(self) -> replicate.Client:

        if self._client is None:

            if not settings.REPLICATE_API_TOKEN:
                raise RuntimeError(
                    "Replicate API token is not configured "
                    "(REPLICATE_API_TOKEN)."
                )

            self._client = replicate.Client(
                api_token=settings.REPLICATE_API_TOKEN,
            )

        return self._client

    # ======================================================
    # Helpers
    # ======================================================

    def _serialize_output(self, output):

        if isinstance(output, list):
            output = output[0]

        if output is None:
            return None

        # Replicate FileOutput -> URL string
        if hasattr(output, "url"):
            try:
                return str(output.url)
            except Exception:
                pass

        # Fallback
        return str(output)

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

        return self.not_supported("chat")

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

        output = self.client.run(
            model,
            input={
                "prompt": prompt,
            },
        )

        return self.response(
            model=model,
            result=self._serialize_output(output),
            metadata={
                "provider": self.name,
            },
        )

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

        output = self.client.run(
            model,
            input={
                "prompt": prompt,
            },
        )

        return self.response(
            model=model,
            result=self._serialize_output(output),
            metadata={
                "provider": self.name,
            },
        )

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

        return self.not_supported("audio")

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

    async def health_check(
        self,
    ) -> bool:

        if not settings.REPLICATE_API_TOKEN:
            return False

        try:

            list(self.client.models.list())

            return True

        except Exception:

            return False