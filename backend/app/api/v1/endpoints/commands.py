from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.ai_request import AIRequest
from app.services.orchestrator.ai_orchestrator import AIOrchestrator

router = APIRouter(
    prefix="/commands",
    tags=["Commands"],
)

orchestrator = AIOrchestrator()


class CommandRequest(BaseModel):
    command: str


@router.post("/run")
async def run_command(request: CommandRequest):

    ai_request = AIRequest(
        prompt=request.command,
        asset_type="text",
    )

    result = await orchestrator.execute(
        agent="chat",
        request=ai_request,
    )

    return result