from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.database.models.workflow import Workflow, WorkflowStep


class WorkflowRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_with_steps(
        self,
        *,
        owner_id: str,
        name: str,
        steps: list[dict],
        project_id: str | None = None,
    ) -> Workflow:
        workflow = Workflow(
            owner_id=owner_id,
            project_id=project_id,
            name=name,
            status="draft",
        )

        for index, step in enumerate(steps):
            workflow.steps.append(
                WorkflowStep(
                    order_index=index,
                    asset_type=step["asset_type"],
                    prompt=step["prompt"],
                    status="pending",
                )
            )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        return workflow

    def get_by_id(self, workflow_id: str) -> Workflow | None:
        return (
            self.db.query(Workflow)
            .options(joinedload(Workflow.steps))
            .filter(Workflow.id == workflow_id)
            .first()
        )

    def list_by_owner(self, owner_id: str) -> list[Workflow]:
        return (
            self.db.query(Workflow)
            .filter(Workflow.owner_id == owner_id)
            .order_by(Workflow.created_at.desc())
            .all()
        )

    def update_workflow_status(self, workflow: Workflow, status: str) -> Workflow:
        workflow.status = status
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def update_step(
        self,
        step: WorkflowStep,
        *,
        status: str,
        asset_id: str | None = None,
        error_message: str | None = None,
    ) -> WorkflowStep:
        step.status = status
        if asset_id is not None:
            step.asset_id = asset_id
        if error_message is not None:
            step.error_message = error_message

        self.db.add(step)
        self.db.commit()
        self.db.refresh(step)

        return step