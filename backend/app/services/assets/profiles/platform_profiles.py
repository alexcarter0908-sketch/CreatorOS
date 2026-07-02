from dataclasses import dataclass


@dataclass(slots=True)
class PlatformProfile:
    platform: str
    width: int
    height: int
    orientation: str
    format: str


PLATFORM_PROFILES = {

    # ---------------- YouTube ----------------

    "youtube_thumbnail": PlatformProfile(
        platform="YouTube",
        width=1280,
        height=720,
        orientation="landscape",
        format="png",
    ),

    "youtube_shorts": PlatformProfile(
        platform="YouTube Shorts",
        width=1080,
        height=1920,
        orientation="vertical",
        format="mp4",
    ),

    "youtube_banner": PlatformProfile(
        platform="YouTube Banner",
        width=2560,
        height=1440,
        orientation="landscape",
        format="png",
    ),

    # ---------------- Instagram ----------------

    "instagram_post": PlatformProfile(
        platform="Instagram",
        width=1080,
        height=1080,
        orientation="square",
        format="png",
    ),

    "instagram_story": PlatformProfile(
        platform="Instagram Story",
        width=1080,
        height=1920,
        orientation="vertical",
        format="png",
    ),

    "instagram_reel": PlatformProfile(
        platform="Instagram Reel",
        width=1080,
        height=1920,
        orientation="vertical",
        format="mp4",
    ),

    "instagram_profile": PlatformProfile(
        platform="Instagram Profile",
        width=320,
        height=320,
        orientation="square",
        format="png",
    ),

    # ---------------- Facebook ----------------

    "facebook_cover": PlatformProfile(
        platform="Facebook",
        width=851,
        height=315,
        orientation="landscape",
        format="png",
    ),

    "facebook_post": PlatformProfile(
        platform="Facebook",
        width=1200,
        height=630,
        orientation="landscape",
        format="png",
    ),

    # ---------------- LinkedIn ----------------

    "linkedin_banner": PlatformProfile(
        platform="LinkedIn",
        width=1584,
        height=396,
        orientation="landscape",
        format="png",
    ),

    "linkedin_post": PlatformProfile(
        platform="LinkedIn",
        width=1200,
        height=627,
        orientation="landscape",
        format="png",
    ),

    # ---------------- X ----------------

    "x_banner": PlatformProfile(
        platform="X",
        width=1500,
        height=500,
        orientation="landscape",
        format="png",
    ),

    "x_post": PlatformProfile(
        platform="X",
        width=1600,
        height=900,
        orientation="landscape",
        format="png",
    ),

    # ---------------- TikTok ----------------

    "tiktok_video": PlatformProfile(
        platform="TikTok",
        width=1080,
        height=1920,
        orientation="vertical",
        format="mp4",
    ),

    "tiktok_profile": PlatformProfile(
        platform="TikTok",
        width=200,
        height=200,
        orientation="square",
        format="png",
    ),

    # ---------------- Generic ----------------

    "logo": PlatformProfile(
        platform="Generic",
        width=1024,
        height=1024,
        orientation="square",
        format="png",
    ),

    "poster": PlatformProfile(
        platform="Generic",
        width=2048,
        height=3072,
        orientation="portrait",
        format="png",
    ),

    "ebook_cover": PlatformProfile(
        platform="Generic",
        width=1600,
        height=2560,
        orientation="portrait",
        format="png",
    ),

    "podcast_cover": PlatformProfile(
        platform="Podcast",
        width=3000,
        height=3000,
        orientation="square",
        format="png",
    ),
}