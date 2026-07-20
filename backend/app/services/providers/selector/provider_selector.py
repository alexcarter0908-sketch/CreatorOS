from __future__ import annotations

from app.schemas.ai_request import AIRequest

from app.services.providers.factory.provider_factory import (
    ProviderFactory,
)

from app.services.providers.registry import (
    MODEL_REGISTRY,
)

from app.services.providers.registry.model import (
    AIModel,
)

from app.services.providers.capabilities import (
    supports_asset_type,
)


class ProviderSelector:
    """
    Enterprise AI Provider Selector

    Priority

    1. Explicit Model
    2. Explicit Provider
    3. Asset Mapping
    4. Capability Ranking
    5. Global Default
    """

    DEFAULT_MODEL = "llama-4-scout"

    ASSET_MAPPING = {
        "text": "llama-4-scout",
        "image": "flux-pro",
        "thumbnail": "flux-pro",
        "poster": "flux-pro",
        "banner": "flux-pro",
        "logo": "flux-pro",
        "profile_photo": "flux-pro",
        "cover": "flux-pro",
        "video": "kling-v2",
        "audio": "eleven-multilingual-v2",
        "voice": "eleven-multilingual-v2",
    }

    def __init__(self):
        self.factory = ProviderFactory()

    # ---------------------------------------------------------

    def get_model(
        self,
        model_id: str,
    ) -> AIModel | None:

        return MODEL_REGISTRY.get(model_id)

    # ---------------------------------------------------------

    def _available(
        self,
        model: AIModel,
    ) -> bool:

        return (
            model.enabled
            and self.factory.has_provider(
                model.provider,
            )
        )

    # ---------------------------------------------------------

    def _capability_candidates(
        self,
        asset_type: str,
    ) -> list[AIModel]:

        candidates = [
            model
            for model in MODEL_REGISTRY.values()
            if (
                self._available(model)
                and supports_asset_type(
                    model,
                    asset_type,
                )
            )
        ]

        candidates.sort(
            key=lambda m: m.priority,
        )

        return candidates

    # ---------------------------------------------------------

    def get_capability_models(
        self,
        capability: str,
    ) -> list[AIModel]:

        attr = f"supports_{capability.lower()}"

        models = [
            model
            for model in MODEL_REGISTRY.values()
            if (
                self._available(model)
                and getattr(
                    model,
                    attr,
                    False,
                )
            )
        ]

        models.sort(
            key=lambda m: m.priority,
        )

        return models

    # ---------------------------------------------------------

    def get_category_models(
        self,
        category: str,
    ) -> list[AIModel]:

        models = [
            model
            for model in MODEL_REGISTRY.values()
            if (
                self._available(model)
                and model.category == category
            )
        ]

        models.sort(
            key=lambda m: m.priority,
        )

        return models

    # ---------------------------------------------------------

    def select(
        self,
        request: AIRequest,
    ) -> AIModel:

        print("=" * 80)
        print("SELECTOR")
        print("=" * 80)

        print("Asset    :", request.asset_type)
        print("Provider :", request.provider)
        print("Model    :", request.model)

        # -------------------------------------------------
        # Explicit Model
        # -------------------------------------------------

        if request.model:

            model = self.get_model(
                request.model,
            )

            if (
                model
                and self._available(model)
                and supports_asset_type(
                    model,
                    request.asset_type,
                )
            ):
                print("Selected explicit model")
                return model

        # -------------------------------------------------
        # Explicit Provider
        # -------------------------------------------------

        if request.provider:

            provider_models = [
                model
                for model in self._capability_candidates(
                    request.asset_type,
                )
                if model.provider == request.provider
            ]

            if provider_models:
                print("Selected explicit provider")
                return provider_models[0]

        # -------------------------------------------------
        # Asset Mapping
        # -------------------------------------------------

        mapped = self.ASSET_MAPPING.get(
            request.asset_type,
        )

        if mapped:

            model = self.get_model(
                mapped,
            )

            if (
                model
                and self._available(model)
                and supports_asset_type(
                    model,
                    request.asset_type,
                )
            ):
                print("Selected mapped model")
                return model

        # -------------------------------------------------
        # Capability Ranking
        # -------------------------------------------------

        candidates = self._capability_candidates(
            request.asset_type,
        )

        if candidates:

            print("Capability Candidates:")

            for item in candidates:

                print(
                    f"{item.priority:03d} | "
                    f"{item.provider:12} | "
                    f"{item.id}"
                )

            return candidates[0]

        # -------------------------------------------------
        # Global Default
        # -------------------------------------------------

        default = self.get_model(
            self.DEFAULT_MODEL,
        )

        if (
            default
            and self._available(default)
            and supports_asset_type(
                default,
                request.asset_type,
            )
        ):
            print("Using global default")
            return default

        # -------------------------------------------------
        # Nothing found - build an informative error
        # -------------------------------------------------

        capable_models = [
            m
            for m in MODEL_REGISTRY.values()
            if supports_asset_type(
                m,
                request.asset_type,
            )
        ]

        if capable_models:

            providers_needed = sorted(
                {
                    m.provider
                    for m in capable_models
                }
            )

            raise RuntimeError(
                f"No available provider for asset '{request.asset_type}'. "
                f"Please configure API key/credits for: "
                f"{', '.join(providers_needed)}."
            )

        raise RuntimeError(
            f"No AI model registered for asset '{request.asset_type}'."
        )