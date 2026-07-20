from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )
    brand_voice: str | None = Field(
        default=None,
        max_length=3000,
    )


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    status: str | None = None
    brand_voice: str | None = Field(
        default=None,
        max_length=3000,
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    owner_id: str
    name: str
    description: str | None
    status: str
    brand_voice: str | None
    created_at: str
    updated_at: str