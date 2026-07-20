from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.asset_repository import AssetRepository
from app.repositories.publish_account_repository import PublishAccountRepository
from app.services.publishing import youtube_service
from app.services.publishing.youtube_service import YouTubeNotConnectedError

router = APIRouter(
    prefix="/publish",
    tags=["Publishing"],
)


class YouTubeUploadRequest(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = "public"
    account_id: str | None = None


@router.get("/accounts")
def list_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists every connected account for every platform (e.g. all YouTube
    channels), so the UI can show them and let the user pick one instead
    of always using whichever was connected first."""
    repo = PublishAccountRepository(db)
    platforms = ["youtube", "instagram", "tiktok", "facebook", "x", "whatsapp"]
    accounts = []
    for platform in platforms:
        for account in repo.list_by_owner_and_platform(current_user.id, platform):
            accounts.append(
                {
                    "id": account.id,
                    "platform": account.platform,
                    "account_label": account.account_label,
                    "external_account_id": account.external_account_id,
                }
            )
    return {"accounts": accounts}


@router.get("/youtube/connect")
def youtube_connect(
    current_user: User = Depends(get_current_user),
):
    try:
        url = youtube_service.build_authorization_url(current_user.id)
    except YouTubeNotConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {"authorization_url": url}


@router.get("/youtube/callback")
def youtube_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    try:
        owner_id = youtube_service.owner_id_from_state(state)
        youtube_service.exchange_code_for_tokens(db, owner_id, code, state)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {"message": "YouTube account connected successfully. You can close this tab."}


@router.post("/youtube/upload/{asset_id}")
def youtube_upload(
    asset_id: str,
    request: YouTubeUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = AssetRepository(db).get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset is not ready (status={asset.status}).",
        )

    try:
        result = youtube_service.upload_video(
            db,
            owner_id=current_user.id,
            asset=asset,
            title=request.title,
            description=request.description,
            tags=request.tags,
            privacy_status=request.privacy_status,
            account_id=request.account_id,
        )
    except YouTubeNotConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return result


@router.get("/download/{asset_id}")
def download_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = AssetRepository(db).get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if not asset.storage_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset has no downloadable file.",
        )

    file_path = Path(asset.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing on disk.",
        )

    ext = file_path.suffix or ".mp4"
    download_name = f"creatoros_{asset.id}{ext}"

    return FileResponse(
        path=str(file_path),
        media_type=asset.mime_type or "application/octet-stream",
        filename=download_name,
    )


