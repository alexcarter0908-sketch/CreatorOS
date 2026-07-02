from dataclasses import dataclass

from app.services.assets.models.asset_types import AssetType


@dataclass(slots=True)
class AssetProfile:
    asset_type: AssetType
    width: int
    height: int
    aspect_ratio: str
    default_format: str
    quality: str
    transparent: bool = False


ASSET_PROFILES = {

    # ==========================
    # YouTube
    # ==========================

    AssetType.THUMBNAIL: AssetProfile(
        asset_type=AssetType.THUMBNAIL,
        width=1280,
        height=720,
        aspect_ratio="16:9",
        default_format="png",
        quality="ultra",
    ),

    AssetType.YOUTUBE_BANNER: AssetProfile(
        asset_type=AssetType.YOUTUBE_BANNER,
        width=2560,
        height=1440,
        aspect_ratio="16:9",
        default_format="png",
        quality="ultra",
    ),

    # ==========================
    # Vertical Video
    # ==========================

    AssetType.SHORTS: AssetProfile(
        asset_type=AssetType.SHORTS,
        width=1080,
        height=1920,
        aspect_ratio="9:16",
        default_format="mp4",
        quality="ultra",
    ),

    AssetType.REELS: AssetProfile(
        asset_type=AssetType.REELS,
        width=1080,
        height=1920,
        aspect_ratio="9:16",
        default_format="mp4",
        quality="ultra",
    ),

    AssetType.TIKTOK: AssetProfile(
        asset_type=AssetType.TIKTOK,
        width=1080,
        height=1920,
        aspect_ratio="9:16",
        default_format="mp4",
        quality="ultra",
    ),

    # ==========================
    # Social
    # ==========================

    AssetType.POST: AssetProfile(
        asset_type=AssetType.POST,
        width=1080,
        height=1080,
        aspect_ratio="1:1",
        default_format="png",
        quality="ultra",
    ),

    AssetType.STORY: AssetProfile(
        asset_type=AssetType.STORY,
        width=1080,
        height=1920,
        aspect_ratio="9:16",
        default_format="png",
        quality="ultra",
    ),

    AssetType.PROFILE_PHOTO: AssetProfile(
        asset_type=AssetType.PROFILE_PHOTO,
        width=1024,
        height=1024,
        aspect_ratio="1:1",
        default_format="png",
        quality="ultra",
    ),

    AssetType.LOGO: AssetProfile(
        asset_type=AssetType.LOGO,
        width=2048,
        height=2048,
        aspect_ratio="1:1",
        default_format="png",
        quality="lossless",
        transparent=True,
    ),

    AssetType.POSTER: AssetProfile(
        asset_type=AssetType.POSTER,
        width=2480,
        height=3508,
        aspect_ratio="A4",
        default_format="png",
        quality="ultra",
    ),

    AssetType.PODCAST_COVER: AssetProfile(
        asset_type=AssetType.PODCAST_COVER,
        width=3000,
        height=3000,
        aspect_ratio="1:1",
        default_format="png",
        quality="lossless",
    ),

    AssetType.UNKNOWN: AssetProfile(
        asset_type=AssetType.UNKNOWN,
        width=1024,
        height=1024,
        aspect_ratio="1:1",
        default_format="png",
        quality="high",
    ),
}


def get_asset_profile(asset_type: AssetType) -> AssetProfile:
    return ASSET_PROFILES.get(
        asset_type,
        ASSET_PROFILES[AssetType.UNKNOWN],
    )