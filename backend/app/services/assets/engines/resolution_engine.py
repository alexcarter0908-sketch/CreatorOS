from dataclasses import dataclass

from app.services.assets.detectors.asset_detector import AssetDetector
from app.services.assets.profiles.platform_profiles import PLATFORM_PROFILES


@dataclass(slots=True)
class ResolutionResult:
    width: int
    height: int
    orientation: str
    format: str


class ResolutionEngine:

    def __init__(self):
        self.detector = AssetDetector()

    def resolve(
        self,
        prompt: str,
    ) -> ResolutionResult:

        detection = self.detector.detect(prompt)

        key_map = {
            ("thumbnail", "youtube"): "youtube_thumbnail",
            ("banner", "generic"): "facebook_cover",
            ("profile_photo", "generic"): "instagram_profile",
            ("poster", "generic"): "poster",
            ("logo", "generic"): "logo",
            ("video", "short_video"): "youtube_shorts",
        }

        profile_key = key_map.get(
            (detection.asset_type, detection.platform)
        )

        if profile_key is None:
            profile_key = "logo"

        profile = PLATFORM_PROFILES[profile_key]

        return ResolutionResult(
            width=profile.width,
            height=profile.height,
            orientation=profile.orientation,
            format=profile.format,
        )