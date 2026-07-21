from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- Create ----------------

    def create(
        self,
        *,
        owner_id: str,
        asset_type: str,
        provider: str,
        model_id: str,
        prompt: str | None = None,
        project_id: str | None = None,
        status: str = "pending",
        source_asset_id: str | None = None,
    ) -> Asset:
        asset = Asset(
            owner_id=owner_id,
            project_id=project_id,
            asset_type=asset_type,
            provider=provider,
            model_id=model_id,
            prompt=prompt,
            status=status,
            source_asset_id=source_asset_id,
        )

        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    # ---------------- Read ----------------

    def get_by_id(
        self,
        asset_id: str,
    ) -> Asset | None:
        return (
            self.db.query(Asset)
            .filter(Asset.id == asset_id)
            .first()
        )

    def list_by_owner(
        self,
        owner_id: str,
        *,
        asset_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Asset]:
        query = self.db.query(Asset).filter(Asset.owner_id == owner_id)

        if asset_type is not None:
            query = query.filter(Asset.asset_type == asset_type)

        return (
            query.order_by(Asset.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def list_by_project(
        self,
        project_id: str,
    ) -> list[Asset]:
        return (
            self.db.query(Asset)
            .filter(Asset.project_id == project_id)
            .order_by(Asset.created_at.desc())
            .all()
        )

    # ---------------- Update lifecycle ----------------

    def mark_completed(
        self,
        asset: Asset,
        *,
        file_url: str,
        storage_path: str,
        mime_type: str | None = None,
        file_size_bytes: int | None = None,
        duration_seconds: float | None = None,
        width: int | None = None,
        height: int | None = None,
        extra_metadata: dict | None = None,
        provider: str | None = None,
        model_id: str | None = None,
    ) -> Asset:
        asset.status = "completed"
        asset.file_url = file_url
        asset.storage_path = storage_path
        asset.mime_type = mime_type
        asset.file_size_bytes = file_size_bytes
        asset.duration_seconds = duration_seconds
        asset.width = width
        asset.height = height
        asset.extra_metadata = extra_metadata
        asset.error_message = None

        if provider:
            asset.provider = provider
        if model_id:
            asset.model_id = model_id

        return self.update(asset)

    def mark_failed(
        self,
        asset: Asset,
        *,
        error_message: str,
    ) -> Asset:
        self.db.rollback()
        asset.status = "failed"
        asset.error_message = error_message

        return self.update(asset)

    def update(
        self,
        asset: Asset,
    ) -> Asset:
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)

        return asset

    def delete(
        self,
        asset: Asset,
    ) -> None:
        self.db.delete(asset)
        self.db.commit()
