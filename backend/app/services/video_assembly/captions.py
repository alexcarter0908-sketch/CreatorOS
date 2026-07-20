from __future__ import annotations

from pathlib import Path

from app.services.video_assembly.schemas import CaptionLine


def _format_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(lines: list[CaptionLine]) -> str:
    blocks = []
    for index, line in enumerate(lines, start=1):
        blocks.append(
            f"{index}\n"
            f"{_format_timestamp(line.start_seconds)} --> "
            f"{_format_timestamp(line.end_seconds)}\n"
            f"{line.text.strip()}\n"
        )
    return "\n".join(blocks)


def write_srt_file(lines: list[CaptionLine], dest_path: Path) -> Path:
    dest_path.write_text(build_srt(lines), encoding="utf-8")
    return dest_path


def ffmpeg_escape_path(path: Path) -> str:
    raw = str(path.resolve())
    raw = raw.replace("\\", "/")
    raw = raw.replace(":", "\\:")
    return raw
