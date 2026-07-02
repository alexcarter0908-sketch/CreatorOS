from dataclasses import dataclass

from app.services.assets.detectors.asset_detector import AssetDetector
from app.services.assets.engines.resolution_engine import ResolutionEngine
from app.services.providers.manager.provider_manager import ProviderManager


@dataclass(slots=True)
class AssetIntelligenceResult:
    asset_type: str
    platform: str
    orientation: str
    width: int
    height: int
    output_format: str
    provider: str
    model: str
    quality: str


class AssetIntelligence:

    def __init__(self):

        self.detector = AssetDetector()
        self.resolution_engine = ResolutionEngine()
        self.provider_manager = ProviderManager()

    def analyze(
        self,
        prompt: str,
    ) -> AssetIntelligenceResult:

        detection = self.detector.detect(prompt)

        resolution = self.resolution_engine.resolve(prompt)

        provider = self.provider_manager.select(
            detection.asset_type,
        )

        return AssetIntelligenceResult(
            asset_type=detection.asset_type,
            platform=detection.platform,
            orientation=detection.orientation,
            width=resolution.width,
            height=resolution.height,
            output_format=resolution.format,
            provider=provider.provider,
            model=provider.model,
            quality=provider.quality,
        )