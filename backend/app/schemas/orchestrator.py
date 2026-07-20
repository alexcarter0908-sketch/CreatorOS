from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestratorRunRequest(BaseModel):
    prompt: str
    project_id: str | None = None
    auto_publish: bool = True
    platforms: list[str] | None = None
    tags: list[str] = Field(default_factory=list)