from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.core.ownership import require_project_ownership
from app.services.workflows.workflow_service import WorkflowService

router = APIRouter(
    prefix="/workflows",
    tags=["Workflows"],
)


class WorkflowStepInput(BaseModel):
    asset_type: str
    prompt: str


class CreateWorkflowRequest(BaseModel):
    name: str
    steps: list[WorkflowStepInput]
    project_id: str | None = None


def serialize_workflow(workflow) -> dict:
    return {
        "id": workflow.id,
        "name": workflow.name,
        "status": workflow.status,
        "project_id": workflow.project_id,
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        "steps": [
            {
                "id": step.id,
                "order_index": step.order_index,
                "asset_type": step.asset_type,
                "prompt": step.prompt,
                "status": step.status,
                "asset_id": step.asset_id,
                "error_message": step.error_message,
            }
            for step in workflow.steps
        ],
    }


@router.post("")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not request.steps:
        raise HTTPException(status_code=400, detail="A workflow needs at least one step.")

    require_project_ownership(db, request.project_id, current_user.id)

    service = WorkflowService(db)
    workflow = service.create(
        owner_id=current_user.id,
        name=request.name,
        steps=[s.model_dump() for s in request.steps],
        project_id=request.project_id,
    )

    return serialize_workflow(workflow)


@router.post("/{workflow_id}/run")
async def run_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkflowService(db)

    try:
        workflow = await service.run(workflow_id, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return serialize_workflow(workflow)


@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkflowService(db)
    workflow = service.repo.get_by_id(workflow_id)

    if workflow is None or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    return serialize_workflow(workflow)


@router.get("")
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WorkflowService(db)
    workflows = service.repo.list_by_owner(current_user.id)
    return [serialize_workflow(w) for w in workflows]