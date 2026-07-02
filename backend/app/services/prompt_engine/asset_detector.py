import re

from app.core.enums import AssetType


class AssetDetector:
    """
    Detects the requested asset type from the user's prompt.

    This is intentionally lightweight.
    In a future version, AI-based detection will be used when
    keyword matching is not confident.
    """

    KEYWORDS = {
        AssetType.TEXT: [
            "write",
            "article",
            "blog",
            "caption",
            "script",
            "story",
            "email",
        ],
        AssetType.IMAGE: [
            "image",
            "picture",
            "photo",
            "art",
        ],
        AssetType.THUMBNAIL: [
            "thumbnail",
            "youtube thumbnail",
        ],
        AssetType.LOGO: [
            "logo",
        ],
        AssetType.POSTER: [
            "poster",
            "flyer",
        ],
        AssetType.BANNER: [
            "banner",
            "cover",
        ],
        AssetType.VIDEO: [
            "video",
            "short",
            "shorts",
            "reel",
            "reels",
            "tiktok",
        ],
        AssetType.AUDIO: [
            "audio",
            "podcast",
        ],
        AssetType.VOICE: [
            "voice",
            "speech",
            "tts",
        ],
    }

    def detect(self, prompt: str) -> str:

        text = prompt.lower()

        text = re.sub(r"\s+", " ", text)

        for asset, keywords in self.KEYWORDS.items():

            if any(keyword in text for keyword in keywords):
                return asset.value

        return AssetType.TEXT.value