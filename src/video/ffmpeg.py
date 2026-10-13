"""Small wrapper around the FFmpeg command line."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from src.utils.errors import LMSError


def ffmpeg_path() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise LMSError(
            "FFmpeg was not found.\n\nThe audio processing and video composition steps require FFmpeg.",
            "Install it with:  winget install --id Gyan.FFmpeg\nthen open a new terminal (PATH changes need a new terminal).",
        )
    return path


def ffprobe_path() -> str:
    """ffprobe ships next to ffmpeg in every FFmpeg build."""
    path = shutil.which("ffprobe")
    if path:
        return path
    sibling = Path(ffmpeg_path()).with_name("ffprobe" + Path(ffmpeg_path()).suffix)
    if sibling.exists():
        return str(sibling)
    raise LMSError("ffprobe was not found (it normally comes with FFmpeg).", "Reinstall FFmpeg: winget install --id Gyan.FFmpeg")


def run_ffmpeg(args: list[str], what: str) -> subprocess.CompletedProcess:
    """Run ``ffmpeg <args>``; raise a readable error mentioning ``what`` on failure."""
    result = subprocess.run([ffmpeg_path(), "-hide_banner", "-y", *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-8:])
        raise LMSError(f"FFmpeg failed while {what}:\n{tail}")
    return result


def media_duration(path: Path) -> float:
    """Duration of an audio/video file in seconds (via ffprobe)."""
    result = subprocess.run(
        [ffprobe_path(), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise LMSError(f"Could not read the duration of {path}.") from exc
