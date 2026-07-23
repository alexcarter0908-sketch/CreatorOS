from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.services.knowledge.knowledge_service import KnowledgeService
from app.schemas.knowledge import KnowledgeDocumentOut
from app.core.config.settings import settings
from app.core.ownership import require_project_ownership

router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge"],
)


@router.post("/upload", response_model=KnowledgeDocumentOut)
async def upload_knowledge_file(
    file: UploadFile = File(...),
    project_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    max_bytes = settings.KNOWLEDGE_MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File {settings.KNOWLEDGE_MAX_FILE_SIZE_MB}MB se bara hai.",
        )

    require_project_ownership(db, project_id, current_user.id)

    service = KnowledgeService(db)
    try:
        doc = service.ingest_file(
            owner_id=current_user.id,
            file_bytes=file_bytes,
            filename=file.filename or "upload",
            mime_type=file.content_type,
            project_id=project_id,
        )
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return doc


@router.get("", response_model=list[KnowledgeDocumentOut])
async def list_knowledge_files(
    project_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = KnowledgeService(db)
    return service.list_documents(current_user.id, project_id=project_id)


@router.delete("/{document_id}")
async def delete_knowledge_file(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = KnowledgeService(db)
    deleted = service.delete_document(current_user.id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document nahi mila.")
    return {"deleted": True}