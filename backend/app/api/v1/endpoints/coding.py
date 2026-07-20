from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends

from app.database.models import User
from app.dependencies.auth import get_current_user
from app.schemas.code_execution import CodeExecutionRequest, CodeExecutionResponse
from app.services.coding.code_executor import run_code

router = APIRouter(
    prefix="/coding",
    tags=["Coding"],
)


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
):
    result = await asyncio.to_thread(run_code, request.language, request.code)
    return CodeExecutionResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
        error=result.error,
    )