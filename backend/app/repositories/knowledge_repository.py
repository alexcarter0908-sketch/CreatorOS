from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models.knowledge import KnowledgeDocument, KnowledgeChunk


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- Documents ----------------

    def create_document(
        self,
        *,
        owner_id: str,
        filename: str,
        project_id: str | None = None,
    ) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            owner_id=owner_id,
            project_id=project_id,
            filename=filename,
            status="processing",
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        return (
            self.db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.id == document_id)
            .first()
        )

    def list_documents(
        self,
        owner_id: str,
        *,
        project_id: str | None = None,
    ) -> list[KnowledgeDocument]:
        query = self.db.query(KnowledgeDocument).filter(KnowledgeDocument.owner_id == owner_id)
        if project_id:
            query = query.filter(KnowledgeDocument.project_id == project_id)
        return query.order_by(KnowledgeDocument.created_at.desc()).all()

    def mark_completed(
        self,
        doc: KnowledgeDocument,
        *,
        file_url: str,
        storage_path: str,
        mime_type: str | None,
        file_size_bytes: int | None,
        chunk_count: int,
    ) -> KnowledgeDocument:
        doc.status = "completed"
        doc.file_url = file_url
        doc.storage_path = storage_path
        doc.mime_type = mime_type
        doc.file_size_bytes = file_size_bytes
        doc.chunk_count = chunk_count
        doc.error_message = None
        return self._save(doc)

    def mark_failed(
        self,
        doc: KnowledgeDocument,
        *,
        error_message: str,
    ) -> KnowledgeDocument:
        self.db.rollback()
        doc.status = "failed"
        doc.error_message = error_message
        return self._save(doc)

    def delete_document(self, doc: KnowledgeDocument) -> None:
        self.db.delete(doc)
        self.db.commit()

    def _save(self, obj):
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ---------------- Chunks ----------------

    def add_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        self.db.add_all(chunks)
        self.db.commit()

    def similarity_search(
        self,
        *,
        owner_id: str,
        query_embedding: list[float],
        project_id: str | None = None,
        top_k: int = 5,
    ) -> list[KnowledgeChunk]:
        query = self.db.query(KnowledgeChunk).filter(KnowledgeChunk.owner_id == owner_id)
        if project_id:
            query = query.filter(KnowledgeChunk.project_id == project_id)
        query = query.order_by(KnowledgeChunk.embedding.cosine_distance(query_embedding))
        return query.limit(top_k).all()
