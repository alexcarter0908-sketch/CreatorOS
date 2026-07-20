from __future__ import annotations

from app.services.providers.capabilities import (
    supports_asset_type,
)

from app.services.providers.fallback.fallback_registry import (
    FALLBACK_REGISTRY,
)

from app.services.providers.registry import (
    MODEL_REGISTRY,
)

from app.services.providers.registry.model import (
    AIModel,
)

from app.services.providers.factory.provider_factory import (
    ProviderFactory,
)


class FallbackResolver:
    """
    Enterprise fallback resolver.

    Responsible for selecting the next valid model
    for an asset type.

    Rules

    1. Registry order
    2. Model enabled
    3. Provider available
    4. Capability supported
    5. Skip already tried models
    """

    def __init__(self):

        self.factory = ProviderFactory()

    # ---------------------------------------------------------

    def resolve(
        self,
        asset_type: str,
        tried: set[tuple[str, str]],
    ) -> AIModel | None:

        chain = FALLBACK_REGISTRY.get(
            asset_type,
            (),
        )

        for model_id in chain:

            model = MODEL_REGISTRY.get(
                model_id,
            )

            if model is None:
                continue

            if not model.enabled:
                continue

            if not self.factory.has_provider(
                model.provider,
            ):
                continue

            if not supports_asset_type(
                model,
                asset_type,
            ):
                continue

            if (
                model.provider,
                model.id,
            ) in tried:
                continue

            return model

        return None