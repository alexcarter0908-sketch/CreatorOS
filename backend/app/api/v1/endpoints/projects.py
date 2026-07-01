from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import (
    create_project,
    get_projects,
    get_project_by_id,
    update_project,
    delete_project,
)

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return get_projects(db)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_by_id(db, project_id)


@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    return create_project(db, project)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_existing_project(
    project_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    return update_project(db, project_id, project)


@router.delete("/{project_id}")
def remove_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    delete_project(db, project_id)
    return {"message": "Project deleted successfully"}