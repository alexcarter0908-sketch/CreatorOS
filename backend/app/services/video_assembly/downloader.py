from __future__ import annotations

import uuid
from pathlib import Path

import httpx


async def download_to_temp(url: str, dest_dir: Path, *, suffix: str = "") -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not suffix:
        guessed = Path(url.split("?")[0]).suffix
        suffix = guessed if guessed else ".bin"

    dest_path = dest_dir / f"{uuid.uuid4().hex}{suffix}"

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=1024 * 256):
                    f.write(chunk)

    return dest_path
