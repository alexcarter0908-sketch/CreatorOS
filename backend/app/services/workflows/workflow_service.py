from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models.workflow import Workflow
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.ai_request import AIRequest
from app.services.assets.asset_service import AssetService
from app.services.orchestrator.ai_orchestrator import AIOrchestrator


class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = WorkflowRepository(db)
        self.asset_service = AssetService(db)
        self.orchestrator = AIOrchestrator()

    def create(
        self,
        *,
        owner_id: str,
        name: str,
        steps: list[dict],
        project_id: str | None = None,
    ) -> Workflow:
        return self.repo.create_with_steps(
            owner_id=owner_id,
            name=name,
            steps=steps,
            project_id=project_id,
        )

    async def run(
        self,
        workflow_id: str,
        owner_id: str,
        seed_text: str | None = None,
        source_asset_id: str | None = None,
    ) -> Workflow:
        """
        Runs every step in order. A failed step is recorded with its
        error and the run continues to the next step - one bad step
        (e.g. a provider missing a permission) does not block the rest
        of the pipeline from being attempted.

        seed_text / source_asset_id are optional: when provided, the
        workflow's first {previous_output} substitution uses this text
        instead of generating it from scratch, and any created assets
        are linked back to that source asset. Both default to None, so
        existing callers are unaffected.

        Final workflow.status is:
          - "completed"             if every step succeeded
          - "completed_with_errors" if at least one step succeeded and
                                     at least one failed
          - "failed"                if every step failed

        A notification is created for the owner once the workflow
        reaches a terminal state, so they know their project finished
        without watching the screen for it.
        """
        workflow = self.repo.get_by_id(workflow_id)

        if workflow is None or workflow.owner_id != owner_id:
            raise ValueError("Workflow not found.")

        self.repo.update_workflow_status(workflow, "running")

        previous_output: str | None = seed_text
        any_success = False
        any_failure = False

        for step in workflow.steps:
            if step.status == "completed":
                previous_output = self._extract_text(step) or previous_output
                any_success = True
                continue

            self.repo.update_step(step, status="running")

            prompt = step.prompt
            if previous_output and "{previous_output}" in prompt:
                prompt = prompt.replace("{previous_output}", previous_output)

            asset = self.asset_service.start(
                owner_id=owner_id,
                asset_type=step.asset_type,
                provider="auto",
                model_id="auto",
                prompt=prompt,
                project_id=workflow.project_id,
                source_asset_id=source_asset_id,
            )

            try:
                ai_request = AIRequest(
                    prompt=prompt,
                    asset_type=step.asset_type,
                    project_id=workflow.project_id,
                )

                result = await self.orchestrator.execute(ai_request)
                asset = self.asset_service.complete_from_provider_result(asset, result)

                self.repo.update_step(step, status="completed", asset_id=asset.id)
                any_success = True

                if asset.asset_type == "text":
                    meta = asset.extra_metadata or {}
                    previous_output = meta.get("text") or previous_output

            except Exception as e:
                any_failure = True
                self.asset_service.fail(asset, error_message=str(e))
                self.repo.update_step(step, status="failed", error_message=str(e))
                # Do NOT return here - move on to the next step so the
                # rest of the pipeline still gets a chance to run.

        if any_success and any_failure:
            final_status = "completed_with_errors"
        elif any_failure:
            final_status = "failed"
        else:
            final_status = "completed"

        self.repo.update_workflow_status(workflow, final_status)

        notif_type, title, message = self._notification_copy(workflow.name, final_status)
        NotificationRepository(self.db).create(
            owner_id=owner_id,
            type=notif_type,
            title=title,
            message=message,
            workflow_id=workflow.id,
        )

        return self.repo.get_by_id(workflow_id)

    def _extract_text(self, step) -> str | None:
        if step.asset_id is None:
            return None
        from app.repositories.asset_repository import AssetRepository

        asset = AssetRepository(self.db).get_by_id(step.asset_id)
        if asset and asset.extra_metadata:
            return asset.extra_metadata.get("text")
        return None

    @staticmethod
    def _notification_copy(name: str, status: str) -> tuple[str, str, str]:
        if status == "completed":
            return (
                "project_completed",
                f'"{name}" is ready',
                "Every step finished successfully.",
            )
        if status == "completed_with_errors":
            return (
                "project_completed_with_errors",
                f'"{name}" finished with some errors',
                "Some steps failed - check the workflow for details.",
            )
        return (
            "project_failed",
            f'"{name}" failed',
            "None of the steps completed. Check the workflow for details.",
        )
