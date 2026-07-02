from dataclasses import dataclass


@dataclass(slots=True)
class AssetDetectionResult:
    asset_type: str
    platform: str
    orientation: str
    confidence: float


class AssetDetector:

    def detect(
        self,
        prompt: str,
    ) -> AssetDetectionResult:

        text = prompt.lower()

        # -------------------------
        # Thumbnail
        # -------------------------

        if any(
            word in text
            for word in [
                "thumbnail",
                "thumb",
                "youtube thumbnail",
                "thambnail",
            ]
        ):
            return AssetDetectionResult(
                asset_type="thumbnail",
                platform="youtube",
                orientation="landscape",
                confidence=0.99,
            )

        # -------------------------
        # Shorts / Reels / TikTok
        # -------------------------

        if any(
            word in text
            for word in [
                "shorts",
                "youtube shorts",
                "reel",
                "reels",
                "instagram reel",
                "tiktok",
            ]
        ):
            return AssetDetectionResult(
                asset_type="video",
                platform="short_video",
                orientation="vertical",
                confidence=0.99,
            )

        # -------------------------
        # Poster
        # -------------------------

        if any(
            word in text
            for word in [
                "poster",
                "flyer",
            ]
        ):
            return AssetDetectionResult(
                asset_type="poster",
                platform="generic",
                orientation="portrait",
                confidence=0.95,
            )

        # -------------------------
        # Banner / Cover
        # -------------------------

        if any(
            word in text
            for word in [
                "banner",
                "cover",
                "facebook cover",
                "linkedin banner",
                "x banner",
                "twitter banner",
            ]
        ):
            return AssetDetectionResult(
                asset_type="banner",
                platform="generic",
                orientation="landscape",
                confidence=0.95,
            )

        # -------------------------
        # Profile Photo
        # -------------------------

        if any(
            word in text
            for word in [
                "profile",
                "profile pic",
                "profile picture",
                "avatar",
                "dp",
            ]
        ):
            return AssetDetectionResult(
                asset_type="profile_photo",
                platform="generic",
                orientation="square",
                confidence=0.95,
            )

        # -------------------------
        # Logo
        # -------------------------

        if any(
            word in text
            for word in [
                "logo",
                "brand mark",
                "company logo",
            ]
        ):
            return AssetDetectionResult(
                asset_type="logo",
                platform="generic",
                orientation="square",
                confidence=0.99,
            )

        # -------------------------
        # Default
        # -------------------------

        return AssetDetectionResult(
            asset_type="text",
            platform="generic",
            orientation="none",
            confidence=0.50,
        )