from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.repositories.knowledge_repository import KnowledgeRepository
from app.services.knowledge.text_extractor import extract_text
from app.services.knowledge.chunker import chunk_text
from app.services.knowledge.embedding_service import embed_texts, embed_query
from app.services.storage import get_storage
from app.core.config.settings import settings


class KnowledgeService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.storage = get_storage()

    def ingest_file(
        self,
        *,
        owner_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None,
        project_id: str | None = None,
    ) -> KnowledgeDocument:
        doc = self.repo.create_document(owner_id=owner_id, filename=filename, project_id=project_id)

        try:
            storage_path, file_url = self.storage.save(
                file_bytes=file_bytes,
                filename=filename,
                subfolder="knowledge",
            )

            text = extract_text(file_bytes=file_bytes, filename=filename, mime_type=mime_type)
            if not text.strip():
                raise ValueError("Is file se koi readable text nahi mila.")

            pieces = chunk_text(text)
            if not pieces:
                raise ValueError("File se chunks nahi ban sakay.")

            embeddings = embed_texts(pieces)

            chunks = [
                KnowledgeChunk(
                    document_id=doc.id,
                    owner_id=owner_id,
                    project_id=project_id,
                    chunk_index=i,
                    content=piece,
                    embedding=embedding,
                )
                for i, (piece, embedding) in enumerate(zip(pieces, embeddings))
            ]
            self.repo.add_chunks(chunks)

            doc = self.repo.mark_completed(
                doc,
                file_url=file_url,
                storage_path=storage_path,
                mime_type=mime_type,
                file_size_bytes=len(file_bytes),
                chunk_count=len(chunks),
            )
        except Exception as exc:
            doc = self.repo.mark_failed(doc, error_message=str(exc))
            raise

        return doc

    def list_documents(self, owner_id: str, *, project_id: str | None = None):
        return self.repo.list_documents(owner_id, project_id=project_id)

    def delete_document(self, owner_id: str, document_id: str) -> bool:
        doc = self.repo.get_document(document_id)
        if not doc or doc.owner_id != owner_id:
            return False
        self.repo.delete_document(doc)
        return True

    def retrieve_context(
        self,
        *,
        owner_id: str,
        query: str,
        project_id: str | None = None,
        top_k: int | None = None,
    ) -> list[KnowledgeChunk]:
        top_k = top_k or settings.KNOWLEDGE_TOP_K
        query_embedding = embed_query(query)
        return self.repo.similarity_search(
            owner_id=owner_id,
            query_embedding=query_embedding,
            project_id=project_id,
            top_k=top_k,
        )
