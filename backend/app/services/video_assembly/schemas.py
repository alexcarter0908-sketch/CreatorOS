from __future__ import annotations

from pydantic import BaseModel, Field


class CaptionLine(BaseModel):
    start_seconds: float
    end_seconds: float
    text: str


class AssemblyClip(BaseModel):
    url: str
    order: int = 0


class AssemblyRequest(BaseModel):
    project_id: str | None = None

    clips: list[AssemblyClip] = Field(default_factory=list)

    voice_over_url: str | None = None
    music_url: str | None = None
    music_volume: float = 0.15

    captions: list[CaptionLine] = Field(default_factory=list)
    burn_captions: bool = True

    width: int = 1080
    height: int = 1920
    fps: int = 30

    platform: str = "generic"
