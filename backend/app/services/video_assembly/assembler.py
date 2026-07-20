from __future__ import annotations

import tempfile
from pathlib import Path

from app.services.video_assembly.captions import write_srt_file, ffmpeg_escape_path
from app.services.video_assembly.downloader import download_to_temp
from app.services.video_assembly.ffmpeg_runner import run_ffmpeg
from app.services.video_assembly.schemas import AssemblyRequest


class VideoAssembler:
    """
    Combines raw provider clips + voice-over + background music + captions
    into a single finished video, using ffmpeg.

    Takes an AssemblyRequest, returns a local Path to the finished .mp4.
    Does NOT touch the database - the caller saves it via AssetService.
    """

    async def assemble(self, request: AssemblyRequest) -> Path:

        if not request.clips:
            raise ValueError("AssemblyRequest needs at least one clip.")

        workdir = Path(tempfile.mkdtemp(prefix="creatoros_assembly_"))

        ordered_clips = sorted(request.clips, key=lambda c: c.order)

        clip_paths: list[Path] = []
        for clip in ordered_clips:
            clip_paths.append(
                await download_to_temp(clip.url, workdir / "clips")
            )

        video_only = await self._concat_clips(
            clip_paths,
            workdir,
            width=request.width,
            height=request.height,
            fps=request.fps,
        )

        with_audio = await self._attach_audio(
            video_only,
            workdir,
            voice_over_url=request.voice_over_url,
            music_url=request.music_url,
            music_volume=request.music_volume,
        )

        final_path = with_audio

        if request.burn_captions and request.captions:
            final_path = await self._burn_captions(
                with_audio,
                workdir,
                request.captions,
            )

        return final_path

    async def _concat_clips(
        self,
        clip_paths: list[Path],
        workdir: Path,
        *,
        width: int,
        height: int,
        fps: int,
    ) -> Path:

        normalized_paths: list[Path] = []

        for index, clip_path in enumerate(clip_paths):
            normalized_path = workdir / f"norm_{index}.mp4"

            await run_ffmpeg(
                [
                    "-i", str(clip_path),
                    "-vf",
                    (
                        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
                        f"fps={fps}"
                    ),
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-an",
                    str(normalized_path),
                ]
            )
            normalized_paths.append(normalized_path)

        concat_list_path = workdir / "concat_list.txt"
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for p in normalized_paths:
                escaped = str(p.resolve()).replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")

        output_path = workdir / "concatenated.mp4"

        await run_ffmpeg(
            [
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_path),
                "-c", "copy",
                str(output_path),
            ]
        )

        return output_path

    async def _attach_audio(
        self,
        video_path: Path,
        workdir: Path,
        *,
        voice_over_url: str | None,
        music_url: str | None,
        music_volume: float,
    ) -> Path:

        if not voice_over_url and not music_url:
            return video_path

        inputs = ["-i", str(video_path)]

        voice_path = None
        music_path = None

        if voice_over_url:
            voice_path = await download_to_temp(voice_over_url, workdir / "audio")
            inputs += ["-i", str(voice_path)]

        if music_url:
            music_path = await download_to_temp(music_url, workdir / "audio")
            inputs += ["-i", str(music_path)]

        output_path = workdir / "with_audio.mp4"

        if voice_path and music_path:
            filter_complex = (
                f"[2:a]volume={music_volume}[music];"
                f"[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
            args = [
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(output_path),
            ]
        elif voice_path:
            args = [
                *inputs,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(output_path),
            ]
        else:
            filter_complex = f"[1:a]volume={music_volume}[aout]"
            args = [
                *inputs,
                "-filter_complex", filter_complex,
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(output_path),
            ]

        await run_ffmpeg(args)

        return output_path

    async def _burn_captions(
        self,
        video_path: Path,
        workdir: Path,
        captions,
    ) -> Path:

        srt_path = write_srt_file(captions, workdir / "captions.srt")
        escaped_srt = ffmpeg_escape_path(srt_path)

        output_path = workdir / "final.mp4"

        await run_ffmpeg(
            [
                "-i", str(video_path),
                "-vf",
                (
                    f"subtitles='{escaped_srt}':"
                    "force_style='FontSize=18,PrimaryColour=&H00FFFFFF,"
                    "OutlineColour=&H00000000,BorderStyle=3,Outline=1'"
                ),
                "-c:a", "copy",
                str(output_path),
            ]
        )

        return output_path
