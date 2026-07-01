from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate


def create_project(db: Session, project: ProjectCreate):
    db_project = Project(
        name=project.name,
        description=project.description,
    )

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project


def get_projects(db: Session):
    return db.query(Project).all()
def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def update_project(db: Session, project_id: int, project: ProjectCreate):
    db_project = get_project_by_id(db, project_id)

    if not db_project:
        return None

    db_project.name = project.name
    db_project.description = project.description

    db.commit()
    db.refresh(db_project)

    return db_project


def delete_project(db: Session, project_id: int):
    db_project = get_project_by_id(db, project_id)

    if not db_project:
        return None

    db.delete(db_project)
    db.commit()

    return db_project