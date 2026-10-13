"""Write subtitle cues as WebVTT (.vtt), the format HTML5 video players use."""

from pathlib import Path

from src.subtitles.srt_generator import srt_time
from src.subtitles.subtitle_config import Cue


def vtt_time(seconds: float) -> str:
    return srt_time(seconds).replace(",", ".")


def write_vtt(cues: list[Cue], path: Path) -> Path:
    blocks = [f"{vtt_time(c.start)} --> {vtt_time(c.end)}\n{c.text}\n" for c in cues]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("WEBVTT\n\n" + "\n".join(blocks), encoding="utf-8")
    return path
