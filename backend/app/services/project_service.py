from sqlalchemy.orm import Session

from app.repositories import project_repository
from app.schemas.project import ProjectCreate


def create_project(db: Session, project: ProjectCreate):
    return project_repository.create_project(db, project)


def get_projects(db: Session):
    return project_repository.get_projects(db)


def get_project_by_id(db: Session, project_id: int):
    return project_repository.get_project_by_id(db, project_id)


def update_project(db: Session, project_id: int, project: ProjectCreate):
    return project_repository.update_project(db, project_id, project)


def delete_project(db: Session, project_id: int):
    return project_repository.delete_project(db, project_id)