from __future__ import annotations

from app.core.config.settings import settings


def chunk_text(
    text: str,
    *,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    chunk_size = chunk_size or settings.KNOWLEDGE_CHUNK_SIZE
    overlap = overlap or settings.KNOWLEDGE_CHUNK_OVERLAP

    text = text.strip()
    if not text:
        return []

    words = text.split()
    chunks: list[str] = []
    start = 0

    approx_words_per_chunk = max(chunk_size // 6, 50)
    approx_overlap_words = max(overlap // 6, 10)

    while start < len(words):
        end = min(start + approx_words_per_chunk, len(words))
        chunk = " ".join(words[start:end])
        if chunk:
            chunks.append(chunk)
        if end == len(words):
            break
        start = end - approx_overlap_words

    return chunks
