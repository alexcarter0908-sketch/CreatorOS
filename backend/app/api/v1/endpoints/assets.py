from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import SessionLocal, get_db
from app.dependencies.auth import get_current_user
from app.repositories.asset_repository import AssetRepository
from app.schemas.ai_request import AIRequest
from app.schemas.asset import (
    AssetResponse,
    AssetRetryRequest,
    AssetStatsResponse,
    AssetTextUpdateRequest,
)
from app.services.billing import credit_service

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)


@router.get("", response_model=list[AssetResponse])
def list_assets(
    asset_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    return repo.list_by_owner(
        current_user.id,
        asset_type=asset_type,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=AssetStatsResponse)
def get_asset_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    assets = repo.list_by_owner(current_user.id, limit=10000, offset=0)

    from app.database.models.billing import BillingAccount
    account = db.query(BillingAccount).filter(BillingAccount.user_id == current_user.id).first()
    credit_balance = account.credit_balance if account else 0

    return AssetStatsResponse(
        scripts=sum(1 for a in assets if a.asset_type == "text"),
        videos=sum(1 for a in assets if a.asset_type == "video"),
        images=sum(1 for a in assets if a.asset_type == "image"),
        audio=sum(1 for a in assets if a.asset_type == "audio"),
        credits=credit_balance,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    return asset


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset_text(
    asset_id: str,
    payload: AssetTextUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit a text-based asset's content in place (e.g. manually tweaking a
    generated script) without re-running the AI provider.
    """
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.asset_type not in ("text", "seo", "script", "document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only text-based assets can be edited.",
        )

    extra_metadata = dict(asset.extra_metadata or {})
    extra_metadata["text"] = payload.text

    asset.extra_metadata = extra_metadata
    asset.status = "completed"
    asset.error_message = None

    return repo.update(asset)


@router.post("/{asset_id}/retry", response_model=AssetResponse)
async def retry_asset(
    asset_id: str,
    payload: AssetRetryRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Re-run generation for an existing asset - used both to retry a failed
    script and to "rewrite" a completed one. Overwrites the same asset row
    (same id) with a fresh AI result so it stays in place in the list.
    """
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    prompt = (payload.prompt if payload else None) or asset.prompt
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No prompt available to retry this asset with.",
        )

    asset.prompt = prompt
    asset.status = "pending"
    asset.error_message = None
    repo.update(asset)

    from app.services.orchestrator.ai_orchestrator import AIOrchestrator

    orchestrator = AIOrchestrator()

    try:
        ai_request = AIRequest(
            prompt=prompt,
            asset_type=asset.asset_type,
            project_id=asset.project_id,
            owner_id=current_user.id,
        )
        result = await orchestrator.execute(ai_request)

        from app.services.assets.asset_service import AssetService

        asset_service = AssetService(db)
        asset = asset_service.complete_from_provider_result(asset, result)
    except Exception as e:
        repo.mark_failed(asset, error_message=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Retry failed: {e}",
        ) from e

    return asset


async def _run_video_workflow_in_background(
    workflow_id: str,
    owner_id: str,
    seed_text: str,
    source_asset_id: str,
) -> None:
    """
    Runs the thumbnail -> video -> SEO workflow in the background using
    an existing script's text as the starting point, so the endpoint
    that kicked this off can return immediately.
    """
    db = SessionLocal()
    try:
        from app.services.workflows.workflow_service import WorkflowService

        service = WorkflowService(db)
        await service.run(
            workflow_id,
            owner_id=owner_id,
            seed_text=seed_text,
            source_asset_id=source_asset_id,
        )
    finally:
        db.close()


@router.post("/{asset_id}/generate-video")
def generate_video_from_script(
    asset_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Turns an already-written script into a video: reuses its text as-is
    (no re-generating the script) and runs thumbnail -> video -> SEO
    as a background workflow. Returns immediately with the workflow id
    so the frontend can poll /api/v1/workflows/{id} for progress.
    """
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.asset_type not in ("text", "seo", "script", "document"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only a script/text asset can be turned into a video.",
        )

    meta = asset.extra_metadata or {}
    script_text = meta.get("text") if isinstance(meta.get("text"), str) else None

    if not script_text or not script_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This script has no generated text yet.",
        )

    label = (asset.prompt or "script")[:50]

    from app.services.workflows.workflow_service import WorkflowService

    service = WorkflowService(db)
    steps = [
        {
            "asset_type": "image",
            "prompt": f"Create a YouTube thumbnail for a video about: {label}. Script context: {{previous_output}}",
        },
        {
            "asset_type": "video",
            "prompt": f"Generate a video based on this script: {{previous_output}}. Original request: {label}",
        },
        {
            "asset_type": "text",
            "prompt": f"Write an SEO-optimized YouTube title, description and tags for: {label}. Script: {{previous_output}}",
        },
    ]

    workflow = service.create(
        owner_id=current_user.id,
        name=f"Video from script: {label}",
        steps=steps,
        project_id=asset.project_id,
    )

    background_tasks.add_task(
        _run_video_workflow_in_background,
        workflow.id,
        current_user.id,
        script_text,
        asset.id,
    )

    return {
        "workflow_id": workflow.id,
        "status": "started",
        "source_asset_id": asset.id,
    }


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AssetRepository(db)
    asset = repo.get_by_id(asset_id)
    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )
    repo.delete(asset)
    return None
