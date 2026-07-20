from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.services.assets.asset_service import AssetService

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


def _detect_kind(content_type: str | None) -> str:
    if not content_type:
        return "document"
    if content_type.startswith("image/"):
        return "image"
    if content_type.startswith("video/"):
        return "video"
    if content_type.startswith("audio/"):
        return "audio"
    return "document"


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    kind = _detect_kind(file.content_type)

    asset_service = AssetService(db)

    asset = asset_service.start(
        owner_id=current_user.id,
        asset_type=kind,
        provider="user_upload",
        model_id="user_upload",
        prompt=None,
    )

    asset = asset_service.complete(
        asset,
        file_bytes=file_bytes,
        filename=file.filename or f"upload-{kind}",
        mime_type=file.content_type,
    )

    return {
        "asset_id": asset.id,
        "file_url": asset.file_url,
        "kind": kind,
    }