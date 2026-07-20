from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Asset
from app.repositories.publish_account_repository import PublishAccountRepository
from app.services.publishing import youtube_service

KNOWN_PLATFORMS = ["youtube", "instagram", "tiktok", "facebook", "x", "whatsapp"]

IMPLEMENTED_PLATFORMS = {"youtube"}


async def publish_to_connected_platforms(
    db: Session,
    *,
    owner_id: str,
    asset: Asset,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    platforms: list[str] | None = None,
) -> dict:
    """
    Publishes the given asset to every platform the user has connected
    (found in publish_accounts), restricted to `platforms` if provided.

    Platforms without a real implementation yet (instagram, tiktok,
    facebook, x, whatsapp) are reported as "connected_but_not_implemented"
    or "not_connected" rather than silently skipped, so the frontend can
    show accurate status. Adding a new platform later only requires:
      1. Building its `_service.py` (like youtube_service.py)
      2. Adding its name to IMPLEMENTED_PLATFORMS
      3. Adding a branch below that calls its upload function
    No orchestrator code needs to change.
    """
    repo = PublishAccountRepository(db)
    target_platforms = platforms or KNOWN_PLATFORMS

    results: dict[str, dict] = {}

    for platform in target_platforms:
        if platform not in KNOWN_PLATFORMS:
            results[platform] = {"status": "unknown_platform"}
            continue

        account = repo.get_by_owner_and_platform(owner_id, platform)

        if account is None:
            results[platform] = {"status": "not_connected"}
            continue

        if platform not in IMPLEMENTED_PLATFORMS:
            results[platform] = {"status": "connected_but_not_implemented"}
            continue

        if platform == "youtube":
            try:
                upload_result = youtube_service.upload_video(
                    db,
                    owner_id=owner_id,
                    asset=asset,
                    title=title,
                    description=description,
                    tags=tags or [],
                    privacy_status="private",
                )
                results[platform] = {"status": "published", **upload_result}
            except Exception as e:
                results[platform] = {"status": "failed", "error": str(e)}

    return results