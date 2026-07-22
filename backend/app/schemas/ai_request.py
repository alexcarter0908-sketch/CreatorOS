from typing import Any
from pydantic import BaseModel, Field
class AIRequest(BaseModel):
    prompt: str
    language: str = "auto"
    asset_type: str = "text"
    purpose: str | None = None
    project_id: str | None = None
    platform: str = "generic"
    provider: str | None = None
    model: str | None = None
    workflow: str | None = None
    quality: str = "ultra"
    speed: str = "balanced"
    creator: str | None = None
    owner_id: str | None = None
    history: list[dict[str, str]] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    latitude: float | None = None
    longitude: float | None = None
    brand_voice: str | None = None
    conversation_id: str | None = None