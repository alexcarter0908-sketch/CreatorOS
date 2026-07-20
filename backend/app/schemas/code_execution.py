from __future__ import annotations

from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    language: str = Field(..., description="python | javascript | bash")
    code: str = Field(..., max_length=50_000)


class CodeExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    error: str | None = None