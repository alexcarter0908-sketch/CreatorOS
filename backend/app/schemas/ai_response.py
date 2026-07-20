from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    """
    Standard response returned by every AI provider.

    Every provider (OpenAI, Gemini, Claude, Groq,
    DeepSeek, Fal, Replicate, Runway, Kling,
    ElevenLabs, etc.) must return this schema.
    """

    success: bool = True

    provider: str

    model: str

    result: Any = None

    language: str = "auto"

    execution_time: float | None = None

    cost: float | None = None

    tokens: int | None = None

    warnings: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)