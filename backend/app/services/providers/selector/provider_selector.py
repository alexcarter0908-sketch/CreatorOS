from app.core.enums import AssetType
from app.services.providers.registry.model_registry import (
    MODEL_REGISTRY,
    AIModel,
)


class ProviderSelector:
    """
    Responsible ONLY for selecting the best model.

    It does NOT:
    - create providers
    - execute providers
    - call APIs
    """

    def select(
        self,
        asset_type: str,
        quality: str = "ultra",
        speed: str = "balanced",
    ) -> AIModel:

        try:
            asset = AssetType(asset_type)
        except ValueError:
            asset = AssetType.TEXT

        mapping = {
            AssetType.TEXT: "gpt-5.5",
            AssetType.IMAGE: "flux-pro",
            AssetType.THUMBNAIL: "flux-pro",
            AssetType.POSTER: "flux-pro",
            AssetType.LOGO: "flux-pro",
            AssetType.BANNER: "flux-pro",
            AssetType.PROFILE_PHOTO: "flux-pro",
            AssetType.VIDEO: "kling-v2",
            AssetType.AUDIO: "elevenlabs-v2",
            AssetType.VOICE: "elevenlabs-v2",
        }

        model_id = mapping.get(asset, "gpt-5.5")

        return MODEL_REGISTRY[model_id]