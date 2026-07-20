from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.auto_target_repository import AutoTargetRepository
from app.schemas.auto_target import AutoTargetCreateRequest, AutoTargetResponse

router = APIRouter(
    prefix="/targets",
    tags=["Auto Targets"],
)


@router.post(
    "",
    response_model=AutoTargetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    request: AutoTargetCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AutoTargetRepository(db)
    return repo.create(
        owner_id=current_user.id,
        asset_type=request.asset_type,
        prompt=request.prompt,
        project_id=request.project_id,
        interval_days=request.interval_days,
        run_at_hour=request.run_at_hour,
        run_at_minute=request.run_at_minute,
        auto_publish=request.auto_publish,
        platforms=request.platforms,
        tags=request.tags,
    )


@router.get(
    "",
    response_model=list[AutoTargetResponse],
)
def list_targets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AutoTargetRepository(db)
    return repo.list_by_owner(current_user.id)


@router.delete(
    "/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_target(
    target_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AutoTargetRepository(db)
    target = repo.get_by_id(target_id)
    if target is None or target.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found.",
        )
    repo.delete(target)
