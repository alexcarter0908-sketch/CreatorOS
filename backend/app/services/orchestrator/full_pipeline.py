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


async def run_full_pipeline(
    db,
    owner_id,
    prompt,
    project_id,
    auto_publish,
    platforms: list[str] | None = None,
    tags: list[str] | None = None,
    workflow_name: str | None = None,
):
    """
    Builds and runs a full script->thumbnail->video->SEO workflow
    synchronously, then (when auto_publish is true) publishes the
    resulting video to every connected platform the caller asked for.
    """
    from app.repositories.asset_repository import AssetRepository
    from app.services.publishing.publish_manager import publish_to_connected_platforms
    from app.services.workflows.workflow_service import WorkflowService

    service = WorkflowService(db)
    steps = [
        {"asset_type": at, "prompt": tpl.replace("{prompt}", prompt)}
        for at, tpl in PIPELINE_STEPS
    ]
    workflow = service.create(
        owner_id=owner_id,
        name=workflow_name or f"Pipeline: {prompt[:50]}",
        steps=steps,
        project_id=project_id,
    )
    workflow = await service.run(workflow.id, owner_id=owner_id)

    result: dict = {"status": workflow.status, "workflow_id": workflow.id}

    if not auto_publish:
        return result

    # PIPELINE_STEPS order is fixed: 0=script, 1=thumbnail, 2=video, 3=SEO text.
    # workflow.steps is always returned ordered by order_index (see Workflow
    # model), so we can address them positionally instead of guessing.
    video_step = workflow.steps[2] if len(workflow.steps) > 2 else None

    if video_step is None or video_step.status != "completed" or not video_step.asset_id:
        result["publish"] = {"status": "skipped", "reason": "video step did not complete"}
        return result

    video_asset = AssetRepository(db).get_by_id(video_step.asset_id)

    if video_asset is None:
        result["publish"] = {"status": "skipped", "reason": "video asset not found"}
        return result

    seo_step = workflow.steps[3] if len(workflow.steps) > 3 else None
    description = ""
    if seo_step and seo_step.status == "completed" and seo_step.asset_id:
        seo_asset = AssetRepository(db).get_by_id(seo_step.asset_id)
        if seo_asset and seo_asset.extra_metadata:
            description = seo_asset.extra_metadata.get("text") or ""

    publish_result = await publish_to_connected_platforms(
        db,
        owner_id=owner_id,
        asset=video_asset,
        title=prompt[:95],
        description=description,
        tags=tags or [],
        platforms=platforms,
    )
    result["publish"] = publish_result

    return result