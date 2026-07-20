from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import imageio_ffmpeg


class FFmpegError(RuntimeError):
    pass


def get_ffmpeg_path() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def _run_ffmpeg_sync(exe: str, args: list[str], cwd: str | None) -> None:
    full_args = [exe, "-y", "-hide_banner", "-loglevel", "error", *args]

    result = subprocess.run(
        full_args,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise FFmpegError(
            f"ffmpeg failed (exit {result.returncode}): "
            f"{result.stderr.decode(errors='ignore')[-2000:]}"
        )


async def run_ffmpeg(args: list[str], *, cwd: Path | None = None) -> None:
    """
    Run ffmpeg with the given arguments (excluding the binary itself).
    Runs in a worker thread so it works regardless of the event loop
    implementation (avoids the Windows Proactor/Selector subprocess issue).
    Raises FFmpegError with stderr output on failure.
    """
    exe = get_ffmpeg_path()

    await asyncio.to_thread(
        _run_ffmpeg_sync,
        exe,
        args,
        str(cwd) if cwd else None,
    )
