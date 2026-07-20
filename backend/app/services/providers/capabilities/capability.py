from __future__ import annotations

from app.services.providers.registry.model import AIModel


class CapabilityFilter:
    """
    Filters models by requested asset capability.
    """

    CAPABILITY_MAP = {
        "text": "supports_text",
        "image": "supports_image",
        "thumbnail": "supports_image",
        "poster": "supports_image",
        "banner": "supports_image",
        "logo": "supports_image",
        "profile_photo": "supports_image",
        "cover": "supports_image",
        "video": "supports_video",
        "audio": "supports_audio",
        "voice": "supports_audio",
        "vision": "supports_vision",
        "embedding": "supports_embeddings",
    }

    @classmethod
    def supports(
        cls,
        model: AIModel,
        asset_type: str,
    ) -> bool:

        capability = cls.CAPABILITY_MAP.get(asset_type)

        if capability is None:
            return True

        return bool(
            getattr(
                model,
                capability,
                False,
            )
        )


# ---------------------------------------------------------
# Backward-compatible helper
# ---------------------------------------------------------

def supports_asset_type(
    model: AIModel,
    asset_type: str,
) -> bool:
    return CapabilityFilter.supports(
        model,
        asset_type,
    )