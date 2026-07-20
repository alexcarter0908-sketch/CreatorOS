from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.orchestrator import OrchestratorRunRequest
from app.services.orchestrator.full_pipeline import run_full_pipeline

router = APIRouter(
    prefix="/orchestrator",
    tags=["Orchestrator"],
)


@router.post("/run")
async def run_orchestrator(
    request: OrchestratorRunRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return await run_full_pipeline(
            db,
            owner_id=current_user.id,
            prompt=request.prompt,
            project_id=request.project_id,
            auto_publish=request.auto_publish,
            platforms=request.platforms,
            tags=request.tags,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
