from __future__ import annotations

import base64
import mimetypes
import uuid
from urllib.parse import urlparse

import requests
from sqlalchemy.orm import Session

from app.database.models import Asset
from app.repositories.asset_repository import AssetRepository
from app.services.storage import get_storage

# Office Open XML types aren't always known to Python's mimetypes
# module by default - register .docx explicitly so a generated Word
# document saves with the right extension instead of ".bin".
mimetypes.add_type(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".docx",
)


class AssetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AssetRepository(db)
        self.storage = get_storage()

    def start(
        self,
        *,
        owner_id: str,
        asset_type: str,
        provider: str,
        model_id: str,
        prompt: str | None = None,
        project_id: str | None = None,
    ) -> Asset:
        return self.repo.create(
            owner_id=owner_id,
            asset_type=asset_type,
            provider=provider,
            model_id=model_id,
            prompt=prompt,
            project_id=project_id,
            status="pending",
        )

    def complete(
        self,
        asset: Asset,
        *,
        file_bytes: bytes,
        filename: str,
        mime_type: str | None = None,
        duration_seconds: float | None = None,
        width: int | None = None,
        height: int | None = None,
        extra_metadata: dict | None = None,
    ) -> Asset:
        storage_path, public_url = self.storage.save(
            file_bytes=file_bytes,
            filename=filename,
            subfolder=asset.asset_type,
        )

        return self.repo.mark_completed(
            asset,
            file_url=public_url,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=len(file_bytes),
            duration_seconds=duration_seconds,
            width=width,
            height=height,
            extra_metadata=extra_metadata,
        )

    def fail(
        self,
        asset: Asset,
        *,
        error_message: str,
    ) -> Asset:
        return self.repo.mark_failed(asset, error_message=error_message)

    def _download_and_rehost(self, url: str, asset_type: str) -> tuple[str, str, str | None, int]:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        file_bytes = response.content
        content_type = response.headers.get("content-type")

        parsed_path = urlparse(url).path
        guessed_name = parsed_path.rsplit("/", 1)[-1] or f"{asset_type}-file"

        if "." not in guessed_name and content_type:
            ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
            if ext:
                guessed_name += ext

        storage_path, public_url = self.storage.save(
            file_bytes=file_bytes,
            filename=guessed_name,
            subfolder=asset_type,
        )

        return storage_path, public_url, content_type, len(file_bytes)

    def _save_data_uri(self, data_uri: str, asset_type: str) -> tuple[str, str, str | None, int]:
        header, _, b64data = data_uri.partition(",")
        content_type = None

        if header.startswith("data:") and ";base64" in header:
            content_type = header[len("data:"):].split(";")[0] or None

        file_bytes = base64.b64decode(b64data)

        ext = mimetypes.guess_extension(content_type) if content_type else None
        filename = f"{asset_type}-{uuid.uuid4().hex}{ext or '.bin'}"

        storage_path, public_url = self.storage.save(
            file_bytes=file_bytes,
            filename=filename,
            subfolder=asset_type,
        )

        return storage_path, public_url, content_type, len(file_bytes)

    def _rehost_any(self, value: str, asset_type: str) -> tuple[str, str, str | None, int]:
        if value.startswith("data:"):
            return self._save_data_uri(value, asset_type)
        return self._download_and_rehost(value, asset_type)

    def complete_from_provider_result(
        self,
        asset: Asset,
        result: dict,
    ) -> Asset:
        payload = result.get("result", result)
        provider_metadata = result.get("metadata", {}) or {}

        real_provider = result.get("provider")
        real_model = result.get("model")

        if asset.asset_type == "text":
            text_value = payload if isinstance(payload, str) else str(payload)
            return self.repo.mark_completed(
                asset,
                file_url="",
                storage_path="",
                extra_metadata={"text": text_value, **provider_metadata},
                provider=real_provider,
                model_id=real_model,
            )

        remote_url = ""
        extra: dict = {}

        if isinstance(payload, list) and payload:
            # Image/video/audio providers that return a list of URLs or
            # data URIs (e.g. OpenRouter's image() method) - use the
            # first item as the primary asset, keep the rest as metadata.
            first = payload[0]
            if isinstance(first, str):
                remote_url = first
            if len(payload) > 1:
                extra["additional_results"] = payload[1:]

        elif isinstance(payload, dict):
            remote_url = payload.get("url") or payload.get("file_url") or ""
            extra = {k: v for k, v in payload.items() if k not in ("url", "file_url")}

        elif isinstance(payload, str) and (
            payload.startswith("http") or payload.startswith("data:")
        ):
            remote_url = payload

        if not remote_url:
            extra["raw_result"] = payload if not isinstance(payload, (dict, list)) else None
            return self.repo.mark_completed(
                asset,
                file_url="",
                storage_path="",
                extra_metadata={**extra, **provider_metadata},
                provider=real_provider,
                model_id=real_model,
            )

        try:
            storage_path, public_url, mime_type, file_size = self._rehost_any(
                remote_url, asset.asset_type
            )
        except Exception as e:
            extra["download_error"] = str(e)
            if not remote_url.startswith("data:"):
                extra["source_url"] = remote_url
            return self.repo.mark_completed(
                asset,
                file_url=remote_url if not remote_url.startswith("data:") else "",
                storage_path="",
                extra_metadata={**extra, **provider_metadata},
                provider=real_provider,
                model_id=real_model,
            )

        if not remote_url.startswith("data:"):
            extra["source_url"] = remote_url

        return self.repo.mark_completed(
            asset,
            file_url=public_url,
            storage_path=storage_path,
            mime_type=mime_type,
            file_size_bytes=file_size,
            extra_metadata={**extra, **provider_metadata},
            provider=real_provider,
            model_id=real_model,
        )