from typing import Any

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    prompt: str

    language: str = "auto"

    asset_type: str = "text"

    platform: str = "generic"

    provider: str | None = None

    model: str | None = None

    workflow: str | None = None

    quality: str = "ultra"

    speed: str = "balanced"

    creator: str | None = None

    attachments: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    preferences: dict[str, Any] = Field(default_factory=dict)