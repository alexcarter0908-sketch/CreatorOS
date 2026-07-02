from typing import Any

from pydantic import BaseModel, Field


class AIResponse(BaseModel):
    success: bool

    provider: str

    model: str

    result: Any

    language: str | None = None

    execution_time: float | None = None

    cost: float | None = None

    tokens: int | None = None

    warnings: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)