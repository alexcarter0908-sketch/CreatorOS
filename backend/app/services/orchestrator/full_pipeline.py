from __future__ import annotations

# (asset_type, prompt_template) - {prompt} is replaced with the user's
# original command, {previous_output} is replaced with the previous
# step's text output (chained automatically by WorkflowService).
PIPELINE_STEPS: list[tuple[str, str]] = [
    ("text", "Write a short, engaging video script for: {prompt}"),
    ("image", "Create a YouTube thumbnail for a video about: {prompt}. Script context: {previous_output}"),
    ("video", "Generate a video based on this script: {previous_output}. Original request: {prompt}"),
    ("text", "Write an SEO-optimized YouTube title, description and tags for: {prompt}. Script: {previous_output}"),
]


async def run_full_pipeline(db, owner_id, prompt, project_id, auto_publish):
    """
    Convenience wrapper kept for backwards compatibility - builds and
    runs a full script->thumbnail->video->SEO workflow synchronously.
    """
    from app.services.workflows.workflow_service import WorkflowService

    service = WorkflowService(db)
    steps = [
        {"asset_type": at, "prompt": tpl.replace("{prompt}", prompt)}
        for at, tpl in PIPELINE_STEPS
    ]
    workflow = service.create(
        owner_id=owner_id,
        name=f"Pipeline: {prompt[:50]}",
        steps=steps,
        project_id=project_id,
    )
    workflow = await service.run(workflow.id, owner_id=owner_id)
    return {"status": workflow.status, "workflow_id": workflow.id}