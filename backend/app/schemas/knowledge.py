from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class KnowledgeDocumentOut(BaseModel):
    id: str
    filename: str
    status: str
    file_url: str | None
    file_size_bytes: int | None
    chunk_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
