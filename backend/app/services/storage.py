from __future__ import annotations

import uuid
from pathlib import Path

from app.core.config.settings import settings


class LocalStorage:
    """
    Simple local-filesystem storage backend.
    Saves files under STORAGE_PATH and returns a public URL built from
    STORAGE_BASE_URL.
    """

    def __init__(self, base_path: str, base_url: str):
        self.base_path = Path(base_path)
        self.base_url = base_url.rstrip("/")

    def save(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        subfolder: str = "",
    ) -> tuple[str, str]:
        folder = self.base_path / subfolder if subfolder else self.base_path
        folder.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4().hex}{ext}"

        file_path = folder / unique_name
        file_path.write_bytes(file_bytes)

        storage_path = str(file_path)
        relative_path = f"{subfolder}/{unique_name}" if subfolder else unique_name
        public_url = f"{self.base_url}/{relative_path}"

        return storage_path, public_url


_storage_instance: LocalStorage | None = None


def get_storage() -> LocalStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = LocalStorage(
            base_path=settings.STORAGE_PATH,
            base_url=settings.STORAGE_BASE_URL,
        )
    return _storage_instance