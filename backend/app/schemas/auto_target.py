from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AutoTargetCreateRequest(BaseModel):
    asset_type: str
    prompt: str
    project_id: str | None = None

    # Fully user-chosen schedule - no defaults forced on the user side
    # beyond sensible fallbacks (daily at 9:00).
    interval_days: int = 1
    run_at_hour: int = 9
    run_at_minute: int = 0

    auto_publish: bool = True
    platforms: list[str] | None = None
    tags: list[str] = Field(default_factory=list)


class AutoTargetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    asset_type: str
    prompt: str
    project_id: str | None
    interval_days: int
    run_at_hour: int
    run_at_minute: int
    auto_publish: bool
    platforms: str | None
    tags: str | None
    is_active: bool
    last_run_at: str | None
    last_run_date: str | None
