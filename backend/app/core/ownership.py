from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Project


def require_project_ownership(
    db: Session,
    project_id: str | None,
    owner_id: str,
) -> Project | None:
    """
    Every endpoint that accepts an optional project_id from the client
    (chat/command requests, conversations, knowledge uploads, automation
    targets, workflows, the orchestrator) must call this before using
    that project_id for anything - otherwise a user could pass another
    user's project_id and have their generated content, brand voice, or
    automation silently attached to someone else's project.

    Returns the Project if project_id is set and belongs to the caller,
    or None if project_id was not provided. Raises 404 if project_id was
    provided but doesn't exist or belongs to someone else - deliberately
    the same response as "not found" rather than 403, so this doesn't
    confirm to an attacker whether a given project_id exists at all.
    """
    if not project_id:
        return None

    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None or project.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project