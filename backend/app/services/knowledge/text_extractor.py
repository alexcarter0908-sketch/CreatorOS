from __future__ import annotations

import io

from pypdf import PdfReader
from docx import Document as DocxDocument


def extract_text(*, file_bytes: bytes, filename: str, mime_type: str | None) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf") or mime_type == "application/pdf":
        return _extract_pdf(file_bytes)

    if lower.endswith(".docx") or mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return _extract_docx(file_bytes)

    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1", errors="ignore")


def _extract_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)


def _extract_docx(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)
