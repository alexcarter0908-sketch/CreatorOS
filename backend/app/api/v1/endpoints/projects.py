from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.project import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
)
from app.services.project import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    request: CreateProjectRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    return service.create(
        current_user.id,
        request,
    )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def list_projects(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    return service.list(current_user.id)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    try:
        return service.get(
            current_user.id,
            project_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    try:
        return service.update(
            current_user.id,
            project_id,
            request,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ProjectService(db)

    try:
        service.delete(
            current_user.id,
            project_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )