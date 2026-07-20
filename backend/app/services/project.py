from __future__ import annotations

from app.database.models import Project
from app.repositories.project_repository import (
    ProjectRepository,
)
from app.schemas.project import (
    CreateProjectRequest,
    UpdateProjectRequest,
)


class ProjectService:
    def __init__(self, db):
        self.projects = ProjectRepository(db)

    def create(
        self,
        owner_id: str,
        request: CreateProjectRequest,
    ) -> Project:
        return self.projects.create(
            owner_id=owner_id,
            name=request.name,
            description=request.description,
            brand_voice=request.brand_voice,
        )

    def list(
        self,
        owner_id: str,
    ) -> list[Project]:
        return self.projects.get_user_projects(
            owner_id,
        )

    def get(
        self,
        owner_id: str,
        project_id: str,
    ) -> Project:

        project = self.projects.get_by_id(project_id)

        if project is None:
            raise ValueError("Project not found.")

        if project.owner_id != owner_id:
            raise ValueError("Project not found.")

        return project

    def update(
        self,
        owner_id: str,
        project_id: str,
        request: UpdateProjectRequest,
    ) -> Project:

        project = self.get(
            owner_id,
            project_id,
        )

        if request.name is not None:
            project.name = request.name

        if request.description is not None:
            project.description = request.description

        if request.status is not None:
            project.status = request.status
        if request.brand_voice is not None:
            project.brand_voice = request.brand_voice
        return self.projects.update(project)

    def delete(
        self,
        owner_id: str,
        project_id: str,
    ) -> None:

        project = self.get(
            owner_id,
            project_id,
        )

        self.projects.delete(project)