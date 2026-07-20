from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset import AssetResponse, AssetStatsResponse
from app.services.billing import credit_service

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


@router.get("", response_model=list[AssetResponse])
def list_assets(
    asset_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    return repo.list_by_owner(
        current_user.id,
        asset_type=asset_type,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=AssetStatsResponse)
def get_asset_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    assets = repo.list_by_owner(current_user.id, limit=10000, offset=0)

    from app.database.models.billing import BillingAccount
    account = db.query(BillingAccount).filter(BillingAccount.user_id == current_user.id).first()
    credit_balance = account.credit_balance if account else 0

    return AssetStatsResponse(
        scripts=sum(1 for a in assets if a.asset_type == "text"),
        videos=sum(1 for a in assets if a.asset_type == "video"),
        images=sum(1 for a in assets if a.asset_type == "image"),
        audio=sum(1 for a in assets if a.asset_type == "audio"),
        credits=credit_balance,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)
    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    repo.delete(asset)
    return None
