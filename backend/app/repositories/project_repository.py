from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Project


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        owner_id: str,
        name: str,
        description: str | None = None,
        brand_voice: str | None = None,
    ) -> Project:
        project = Project(
            owner_id=owner_id,
            name=name,
            description=description,
            brand_voice=brand_voice,
        )

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def get_by_id(
        self,
        project_id: str,
    ) -> Project | None:
        return (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    def get_user_projects(
        self,
        owner_id: str,
    ) -> list[Project]:
        return (
            self.db.query(Project)
            .filter(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    def update(
        self,
        project: Project,
    ) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        return project

    def promote_to_active_if_auto(
        self,
        project_id: str,
    ) -> Project | None:
        """Move a project from draft -> active once it has real content,
        but only if the user hasn't manually pinned its status."""
        project = self.get_by_id(project_id)

        if project is None:
            return None

        if project.status_auto and project.status == "draft":
            project.status = "active"
            return self.update(project)

        return project

    def delete(
        self,
        project: Project,
    ) -> None:
        self.db.delete(project)
        self.db.commit()
