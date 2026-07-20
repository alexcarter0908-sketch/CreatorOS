from dataclasses import dataclass

from app.services.assets.models.asset_context import AssetContext


@dataclass(slots=True, frozen=True)
class QualityResult:
    quality: str


class QualityEngine:
    """
    Determines output quality for an asset.

    Future:
    - User subscription
    - Provider capabilities
    - Cost optimization
    - Performance optimization
    """

    def resolve(
        self,
        context: AssetContext,
    ) -> QualityResult:

        return QualityResult(
            quality=context.quality,
        )