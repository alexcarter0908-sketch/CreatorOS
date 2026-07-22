from __future__ import annotations

"""
Platform-aware media sizing.

Different platforms expect different shapes for the same "purpose"
(a YouTube thumbnail is not the same shape as a Facebook cover photo,
which is not the same shape as a TikTok cover). This module is the
single place that knows those shapes, so every provider asks the same
question the same way instead of hard-coding one platform's numbers.

Nothing here is YouTube-specific by design - add a new platform or
purpose by adding a row below, no provider code needs to change.
"""

# (width, height) in pixels, per platform, per purpose.
IMAGE_SPECS: dict[str, dict[str, tuple[int, int]]] = {
    "youtube": {
        "thumbnail": (1280, 720),
        "banner": (2560, 1440),
        "cover": (2560, 1440),
        "profile_photo": (800, 800),
        "logo": (800, 800),
        "image": (1280, 720),
    },
    "facebook": {
        "cover": (820, 312),
        "banner": (820, 312),
        "profile_photo": (170, 170),
        "logo": (170, 170),
        "thumbnail": (1200, 630),
        "poster": (1200, 630),
        "image": (1200, 630),
    },
    "instagram": {
        "post": (1080, 1080),
        "thumbnail": (1080, 1080),
        "cover": (1080, 1080),
        "story": (1080, 1920),
        "profile_photo": (320, 320),
        "logo": (320, 320),
        "banner": (1080, 1080),
        "image": (1080, 1080),
    },
    "tiktok": {
        "cover": (1080, 1920),
        "thumbnail": (1080, 1920),
        "banner": (1080, 1920),
        "profile_photo": (200, 200),
        "logo": (200, 200),
        "image": (1080, 1920),
    },
    # Used whenever the caller doesn't specify a platform (or specifies
    # one we don't know yet) - a safe, widely-usable default per purpose.
    "generic": {
        "thumbnail": (1280, 720),
        "banner": (1920, 1080),
        "cover": (1920, 1080),
        "poster": (1080, 1350),
        "profile_photo": (512, 512),
        "logo": (512, 512),
        "post": (1080, 1080),
        "image": (1024, 1024),
    },
}

# Kling only accepts a small fixed set of video aspect ratios.
VIDEO_ASPECT_RATIOS: dict[str, str] = {
    "youtube": "16:9",
    "facebook": "16:9",
    "instagram": "9:16",
    "tiktok": "9:16",
    "generic": "16:9",
}


def resolve_image_dimensions(
    asset_type: str | None,
    platform: str | None,
) -> tuple[int, int]:
    """
    Resolves the (width, height) to generate an image at, based on
    what it's *for* (asset_type: thumbnail/banner/cover/profile_photo/...)
    and *where* it's going (platform: youtube/facebook/instagram/tiktok).
    Falls back gracefully if either is missing or unrecognised.
    """
    platform_key = (platform or "generic").strip().lower()
    purpose_key = (asset_type or "image").strip().lower()

    specs = IMAGE_SPECS.get(platform_key, IMAGE_SPECS["generic"])

    if purpose_key in specs:
        return specs[purpose_key]

    # Known platform, but this purpose isn't defined for it - use that
    # platform's own default shape rather than falling all the way back
    # to generic (a Facebook image should stay Facebook-shaped).
    if "image" in specs:
        return specs["image"]

    return IMAGE_SPECS["generic"]["image"]


def resolve_video_aspect_ratio(platform: str | None) -> str:
    return VIDEO_ASPECT_RATIOS.get((platform or "generic").strip().lower(), "16:9")


def fit_within(
    width: int,
    height: int,
    max_side: int = 1440,
    multiple: int = 16,
) -> tuple[int, int]:
    """
    Scales (width, height) down (never up) so the longest side is at
    most `max_side`, then rounds both sides to the nearest `multiple`
    (most diffusion models require dimensions divisible by 8 or 16).
    Keeps the resolver free to use exact real-world platform sizes
    (some of which are larger than a model's max resolution) without
    every provider needing its own clamping logic.
    """
    scale = min(1.0, max_side / max(width, height))
    scaled_w = max(multiple, round(width * scale / multiple) * multiple)
    scaled_h = max(multiple, round(height * scale / multiple) * multiple)
    return scaled_w, scaled_h