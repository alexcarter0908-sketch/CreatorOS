from fastapi import APIRouter

from app.schemas.command import (
    CommandRequest,
    CommandResponse,
)
from app.services.ai.command_service import CommandService

router = APIRouter(
    prefix="/commands",
    tags=["Commands"],
)

service = CommandService()


@router.post(
    "/execute",
    response_model=CommandResponse,
)
def execute(request: CommandRequest):
    result = service.execute(
        request.projectId,
        request.command,
    )

    return CommandResponse(
        executionId=result["executionId"],
        status=result["status"],
    )