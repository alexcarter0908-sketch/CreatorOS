from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AssetTextUpdateRequest(BaseModel):
    text: str


class AssetRetryRequest(BaseModel):
    prompt: str | None = None


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    asset_type: str
    provider: str
    model_id: str
    prompt: str | None
    status: str
    file_url: str | None
    extra_metadata: dict | None
    error_message: str | None
    source_asset_id: str | None = None
    created_at: datetime
    updated_at: datetime


class AssetStatsResponse(BaseModel):
    scripts: int
    videos: int
    images: int
    audio: int
    credits: int